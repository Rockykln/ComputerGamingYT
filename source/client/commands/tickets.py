from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.ticket_config import config, save_config

class TicketView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.select(
		placeholder="Wähle einen Grund für dein Ticket",
		options=[
			discord.SelectOption(label="Allgemeine Hilfe", value="general", description="Allgemeine Fragen und Hilfe"),
			discord.SelectOption(label="Technischer Support", value="technical", description="Technische Probleme"),
			discord.SelectOption(label="Beschwerde", value="complaint", description="Eine Beschwerde einreichen"),
			discord.SelectOption(label="Sonstiges", value="other", description="Andere Anliegen")
		]
	)
	async def ticket_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
		guild_id = str(interaction.guild_id)
		
		category_id = config['support_categories'].get(guild_id)
		category = interaction.guild.get_channel(category_id)
		if not category:
			category = await interaction.guild.create_category("Support-Tickets")
			config['support_categories'][guild_id] = category.id
			save_config(config)

		if guild_id not in config['ticket_counter']:
			config['ticket_counter'][guild_id] = 0
		config['ticket_counter'][guild_id] += 1
		ticket_number = config['ticket_counter'][guild_id]
		
		channel_name = f"ticket-{ticket_number:04d}"
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

		config['active_tickets'][str(ticket_channel.id)] = {
			"user_id": interaction.user.id,
			"claimed_by": None,
			"reason": select.values[0]
		}
		save_config(config)

		claim_view = TicketClaimView(ticket_channel)
		embed = discord.Embed(
			title=f"Ticket #{ticket_number:04d}",
			description=f"Ticket erstellt von {interaction.user.mention}\nGrund: {select.values[0]}",
			color=discord.Color.blue()
		)
		await ticket_channel.send(embed=embed, view=claim_view)
		await interaction.response.send_message(f"Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)

class TicketClaimView(discord.ui.View):
	def __init__(self, ticket_channel):
		super().__init__(timeout=None)
		self.ticket_channel = ticket_channel

	@discord.ui.button(label="Ticket übernehmen", style=discord.ButtonStyle.green, custom_id="claim_ticket")
	async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		ticket_id = str(self.ticket_channel.id)
		if ticket_id not in config['active_tickets']:
			await interaction.response.send_message("Dieses Ticket existiert nicht mehr!", ephemeral=True)
			return

		if not interaction.user.guild_permissions.manage_channels:
			await interaction.response.send_message("Du hast keine Berechtigung, Tickets zu übernehmen!", ephemeral=True)
			return

		ticket_info = config['active_tickets'][ticket_id]
		if ticket_info['claimed_by']:
			if ticket_info['claimed_by'] == interaction.user.id:

				ticket_info['claimed_by'] = None
				button.label = "Ticket übernehmen"
				button.style = discord.ButtonStyle.green
				await interaction.response.send_message("Du hast das Ticket freigegeben.", ephemeral=True)
			else:
				claimer = interaction.guild.get_member(ticket_info['claimed_by'])
				await interaction.response.send_message(
					f"Dieses Ticket wurde bereits von {claimer.mention} übernommen!",
					ephemeral=True
				)
		else:

			ticket_info['claimed_by'] = interaction.user.id
			button.label = "Ticket freigeben"
			button.style = discord.ButtonStyle.red
			await interaction.response.send_message("Du hast das Ticket übernommen!", ephemeral=True)

		save_config(config)
		await interaction.message.edit(view=self)

def setup(tree: app_commands.CommandTree, server_id: str):
	
	@tree.command(
		name="setupsupport",
		description="Richtet den Support-Kanal ein",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def setupsupport(interaction: discord.Interaction, channel: discord.TextChannel):
		guild_id = str(interaction.guild_id)
		config['ticket_channels'][guild_id] = channel.id
		save_config(config)
		
		embed = discord.Embed(
			title="🎫 Support-Ticket erstellen",
			description="Klicke auf das Dropdown-Menü unten, um ein Support-Ticket zu erstellen.",
			color=discord.Color.blue()
		)
		
		await channel.send(embed=embed, view=TicketView())
		await interaction.response.send_message("Support-System wurde eingerichtet!", ephemeral=True)

	@tree.command(
		name="closeticket",
		description="Schließt das aktuelle Ticket",
		guild=discord.Object(id=server_id)
	)
	async def closeticket(interaction: discord.Interaction):
		channel_id = str(interaction.channel.id)
		if channel_id not in config['active_tickets']:
			await interaction.response.send_message("Dies ist kein Ticket-Kanal!", ephemeral=True)
			return

		ticket_info = config['active_tickets'][channel_id]
		if interaction.user.id != ticket_info['user_id'] and not interaction.user.guild_permissions.manage_channels:
			await interaction.response.send_message("Du kannst dieses Ticket nicht schließen!", ephemeral=True)
			return

		del config['active_tickets'][channel_id]
		save_config(config)
		await interaction.channel.delete()