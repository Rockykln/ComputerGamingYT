from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.voice_config import config, save_config

class VoiceSettingsView(discord.ui.View):
	def __init__(self, channel, owner):
		super().__init__(timeout=None)
		self.channel = channel
		self.owner = owner

	@discord.ui.select(
		placeholder="Wähle eine Einstellung",
		options=[
			discord.SelectOption(label="Name ändern", value="name", description="Ändere den Namen des Kanals"),
			discord.SelectOption(label="Limit ändern", value="limit", description="Ändere das Benutzerlimit"),
			discord.SelectOption(label="Kanal sperren", value="lock", description="Sperre den Kanal für andere"),
			discord.SelectOption(label="Kanal entsperren", value="unlock", description="Entsperre den Kanal")
		]
	)
	async def settings_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
		if interaction.user.id != self.owner:
			await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals!", ephemeral=True)
			return

		if select.values[0] == "name":
			await interaction.response.send_modal(ChannelNameModal(self.channel))
		elif select.values[0] == "limit":
			await interaction.response.send_modal(UserLimitModal(self.channel))
		elif select.values[0] == "lock":
			await self.channel.set_permissions(interaction.guild.default_role, connect=False)
			await interaction.response.send_message("Kanal wurde gesperrt!", ephemeral=True)
		elif select.values[0] == "unlock":
			await self.channel.set_permissions(interaction.guild.default_role, connect=True)
			await interaction.response.send_message("Kanal wurde entsperrt!", ephemeral=True)

class ChannelNameModal(discord.ui.Modal, title="Kanal umbenennen"):
	def __init__(self, channel):
		super().__init__()
		self.channel = channel
		self.name = discord.ui.TextInput(
			label="Neuer Name",
			placeholder="Gib den neuen Namen ein",
			min_length=1,
			max_length=32
		)
		self.add_item(self.name)

	async def on_submit(self, interaction: discord.Interaction):
		await self.channel.edit(name=f"🎮 {self.name.value}")
		await interaction.response.send_message(f"Kanalname wurde zu '{self.name.value}' geändert!", ephemeral=True)

class UserLimitModal(discord.ui.Modal, title="Benutzerlimit ändern"):
	def __init__(self, channel):
		super().__init__()
		self.channel = channel
		self.limit = discord.ui.TextInput(
			label="Neues Limit",
			placeholder="Gib das neue Limit ein (0-99)",
			min_length=1,
			max_length=2
		)
		self.add_item(self.limit)

	async def on_submit(self, interaction: discord.Interaction):
		try:
			limit = int(self.limit.value)
			if 0 <= limit <= 99:
				await self.channel.edit(user_limit=limit)
				await interaction.response.send_message(f"Benutzerlimit wurde auf {limit} gesetzt!", ephemeral=True)
			else:
				await interaction.response.send_message("Das Limit muss zwischen 0 und 99 liegen!", ephemeral=True)
		except ValueError:
			await interaction.response.send_message("Bitte gib eine gültige Zahl ein!", ephemeral=True)

def setup(tree: app_commands.CommandTree, server_id: str):
	
	@tree.command(
		name="setjoinvoice",
		description="Setzt den Join-für-Channel Kanal",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def setjoinvoice(interaction: Interaction, channel: discord.VoiceChannel):
		guild_id = str(interaction.guild_id)
		config['join_channels'][guild_id] = channel.id
		save_config(config)
		await interaction.response.send_message(f"Join-für-Channel wurde auf {channel.name} gesetzt!")

	@client.event
	async def on_voice_state_update(member, before, after):
		if member.bot:
			return

		guild_id = str(member.guild.id)
		
		if after and after.channel:
			join_channel_id = config['join_channels'].get(guild_id)
			if join_channel_id and after.channel.id == join_channel_id:
				category = after.channel.category
				new_channel = await member.guild.create_voice_channel(
					name=f"🎮 {member.display_name}s Channel",
					category=category,
					user_limit=5
				)
				await member.move_to(new_channel)
				config['temp_channels'][str(new_channel.id)] = member.id
				save_config(config)

				view = VoiceSettingsView(new_channel, member.id)
				await new_channel.send(
					f"Willkommen in deinem Sprachkanal, {member.mention}!\n"
					"Nutze das Dropdown-Menü unten, um die Einstellungen zu ändern:",
					view=view
				)


		if before and before.channel:
			channel_id = str(before.channel.id)
			if channel_id in config['temp_channels']:
				if len(before.channel.members) == 0:

					await before.channel.delete()

					del config['temp_channels'][channel_id]
					save_config(config)


