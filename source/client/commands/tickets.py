from source.client.config.imports import *
from source.client.config.client import client

tickets = {}
ticket_counter = {}

class TicketView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)  
		self.add_item(self.create_dropdown())

	def create_dropdown(self):
		options = [
			discord.SelectOption(
				label="Allgemeine Hilfe",
				value="general",
				description="Allgemeine Fragen und Hilfe",
				emoji="❓"
			),
			discord.SelectOption(
				label="Technischer Support",
				value="technical",
				description="Technische Probleme",
				emoji="🔧"
			),
			discord.SelectOption(
				label="Beschwerde",
				value="complaint",
				description="Eine Beschwerde einreichen",
				emoji="📝"
			),
			discord.SelectOption(
				label="Sonstiges",
				value="other",
				description="Andere Anliegen",
				emoji="📌"
			)
		]
		
		select = discord.ui.Select(
			placeholder="Wähle einen Grund für dein Ticket",
			options=options,
			custom_id="ticket_select"
		)
		select.callback = self.select_callback
		return select

	async def select_callback(self, interaction: discord.Interaction):
		guild_id = str(interaction.guild_id)
		
		if guild_id not in ticket_counter:
			ticket_counter[guild_id] = 0
		ticket_counter[guild_id] += 1

		category = discord.utils.get(interaction.guild.categories, name="Support-Tickets")
		if not category:
			category = await interaction.guild.create_category("Support-Tickets")

		channel_name = f"ticket-{ticket_counter[guild_id]:04d}"
		overwrites = {
			interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
			interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
		}

		ticket_channel = await interaction.guild.create_text_channel(
			name=channel_name,
			category=category,
			overwrites=overwrites
		)

		tickets[str(ticket_channel.id)] = {
			"user_id": interaction.user.id,
			"claimed_by": None,
			"reason": interaction.data["values"][0]
		}

		claim_view = TicketClaimView()
		
		embed = discord.Embed(
			title=f"Ticket #{ticket_counter[guild_id]:04d}",
			description=f"Ticket erstellt von {interaction.user.mention}\nGrund: {interaction.data['values'][0]}",
			color=discord.Color.blue()
		)
		
		await ticket_channel.send(embed=embed, view=claim_view)
		await interaction.response.send_message(
			f"Dein Ticket wurde erstellt: {ticket_channel.mention}",
			ephemeral=True
		)

class TicketClaimView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(
		label="Ticket übernehmen",
		style=discord.ButtonStyle.green,
		custom_id="claim_ticket"
	)
	async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		ticket_id = str(interaction.channel.id)
		if ticket_id not in tickets:
			await interaction.response.send_message(
				"Dieses Ticket existiert nicht mehr!",
				ephemeral=True
			)
			return

		if not interaction.user.guild_permissions.manage_channels:
			await interaction.response.send_message(
				"Du hast keine Berechtigung, Tickets zu übernehmen!",
				ephemeral=True
			)
			return

		ticket_info = tickets[ticket_id]
		if ticket_info["claimed_by"] == interaction.user.id:
			ticket_info["claimed_by"] = None
			button.label = "Ticket übernehmen"
			button.style = discord.ButtonStyle.green
			await interaction.response.send_message(
				"Du hast das Ticket freigegeben.",
				ephemeral=True
			)
		elif ticket_info["claimed_by"]:
			claimer = interaction.guild.get_member(ticket_info["claimed_by"])
			await interaction.response.send_message(
				f"Dieses Ticket wurde bereits von {claimer.mention} übernommen!",
				ephemeral=True
			)
		else:
			ticket_info["claimed_by"] = interaction.user.id
			button.label = "Ticket freigeben"
			button.style = discord.ButtonStyle.red
			await interaction.response.send_message(
				"Du hast das Ticket übernommen!",
				ephemeral=True
			)

		await interaction.message.edit(view=self)

def setup(tree: app_commands.CommandTree, server_id: str):
	@tree.command(
		name="setupsupport",
		description="Richtet den Support-Kanal ein",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def setupsupport(interaction: discord.Interaction, channel: discord.TextChannel):
		embed = discord.Embed(
			title="🎫 Support-Ticket erstellen",
			description="Klicke auf das Dropdown-Menü unten, um ein Support-Ticket zu erstellen.",
			color=discord.Color.blue()
		)

		view = TicketView()
		await channel.send(embed=embed, view=view)
		await interaction.response.send_message("Support-System wurde eingerichtet!", ephemeral=True)

	client.add_view(TicketView())
	client.add_view(TicketClaimView())