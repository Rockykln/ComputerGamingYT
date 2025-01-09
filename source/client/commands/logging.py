from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.logging_config import save_logging_channel, get_logging_channel

async def send_log(guild_id: int, embed: Embed):
	"""Send a log message to the configured logging channel"""
	channel_id = get_logging_channel(guild_id)
	if channel_id:
		channel = client.get_channel(channel_id)
		if channel:
			await channel.send(embed=embed)

def setup(tree: app_commands.CommandTree, server_id: str):
	@tree.command(
		name="setlogchannel",
		description="Setzt den Kanal für Bot-Logs (nur Admin)",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def setlogchannel(interaction: Interaction, channel: TextChannel):
		save_logging_channel(interaction.guild_id, channel.id)
		await interaction.response.send_message(f"Log-Kanal wurde auf {channel.mention} gesetzt!")

	@client.event
	async def on_message_delete(message):
		if not message.author.bot:
			embed = Embed(title="Nachricht gelöscht", color=discord.Color.red())
			embed.add_field(name="Autor", value=str(message.author), inline=True)
			embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
			embed.add_field(name="Inhalt", value=message.content or "Kein Inhalt", inline=False)
			embed.timestamp = datetime.now()
			await send_log(message.guild.id, embed)

	@client.event
	async def on_member_join(member):
		embed = Embed(title="Mitglied beigetreten", color=discord.Color.green())
		embed.add_field(name="Mitglied", value=str(member), inline=True)
		embed.add_field(name="ID", value=member.id, inline=True)
		embed.timestamp = datetime.now()
		await send_log(member.guild.id, embed)

	@client.event
	async def on_member_remove(member):
		embed = Embed(title="Mitglied verlassen", color=discord.Color.red())
		embed.add_field(name="Mitglied", value=str(member), inline=True)
		embed.add_field(name="ID", value=member.id, inline=True)
		embed.timestamp = datetime.now()
		await send_log(member.guild.id, embed)

	@client.event
	async def on_voice_state_update(member, before, after):
		if before.channel != after.channel:
			embed = Embed(title="Sprachchannel Update", color=discord.Color.blue())
			embed.add_field(name="Mitglied", value=str(member), inline=True)
			if before.channel:
				embed.add_field(name="Verlassen", value=before.channel.name, inline=True)
			if after.channel:
				embed.add_field(name="Beigetreten", value=after.channel.name, inline=True)
			embed.timestamp = datetime.now()
			await send_log(member.guild.id, embed)

	@client.event
	async def on_guild_channel_create(channel):
		embed = Embed(title="Channel erstellt", color=discord.Color.green())
		embed.add_field(name="Name", value=channel.name, inline=True)
		embed.add_field(name="Typ", value=str(channel.type), inline=True)
		embed.timestamp = datetime.now()
		await send_log(channel.guild.id, embed)

	@client.event
	async def on_guild_channel_delete(channel):
		embed = Embed(title="Channel gelöscht", color=discord.Color.red())
		embed.add_field(name="Name", value=channel.name, inline=True)
		embed.add_field(name="Typ", value=str(channel.type), inline=True)
		embed.timestamp = datetime.now()
		await send_log(channel.guild.id, embed)