from source.client.config.imports import *
from source.client.config.client import client

def get_size(bytes, suffix="B"):
	factor = 1024
	for unit in ["", "K", "M", "G", "T", "P"]:
		if bytes < factor:
			return f"{bytes:.2f}{unit}{suffix}"
		bytes /= factor

def setup(tree: app_commands.CommandTree, server_id: str):
	
	@tree.command(
		name="sysinfo",
		description="Zeigt Systeminformationen an",
		guild=discord.Object(id=server_id)
	)
	async def sysinfo(interaction: Interaction):
		try:
			embed = Embed(title="🖥️ Systeminformationen", color=discord.Color.blue())
			
			cpu_freq = psutil.cpu_freq()
			cpu_usage = psutil.cpu_percent(interval=1)
			embed.add_field(
				name="CPU",
				value=f"```\nModell: {platform.processor()}\n"
					  f"Nutzung: {cpu_usage}%\n"
					  f"Frequenz: {cpu_freq.current:.2f}MHz```",
				inline=False
			)
			
			mem = psutil.virtual_memory()
			embed.add_field(
				name="RAM",
				value=f"```\nGesamt: {get_size(mem.total)}\n"
					  f"Verfügbar: {get_size(mem.available)}\n"
					  f"Genutzt: {mem.percent}%```",
				inline=False
			)
			
			disk = psutil.disk_usage('/')
			embed.add_field(
				name="Festplatte",
				value=f"```\nGesamt: {get_size(disk.total)}\n"
					  f"Verfügbar: {get_size(disk.free)}\n"
					  f"Genutzt: {disk.percent}%```",
				inline=False
			)
			
			await interaction.response.send_message(embed=embed)
			
		except Exception as e:
			await interaction.response.send_message(f"Fehler beim Abrufen der Systeminformationen: {str(e)}")

	@tree.command(
		name="drives",
		description="Zeigt Informationen über alle Laufwerke",
		guild=discord.Object(id=server_id)
	)
	async def drives(interaction: Interaction):
		try:
			embed = Embed(title="💾 Laufwerksinformationen", color=discord.Color.blue())
			
			partitions = psutil.disk_partitions()
			for partition in partitions:
				try:
					partition_usage = psutil.disk_usage(partition.mountpoint)
					embed.add_field(
						name=f"Laufwerk {partition.device}",
						value=f"```\nDateisystem: {partition.fstype}\n"
							  f"Gesamt: {get_size(partition_usage.total)}\n"
							  f"Genutzt: {partition_usage.percent}%```",
						inline=False
					)
				except Exception:
					continue
			
			await interaction.response.send_message(embed=embed)
			
		except Exception as e:
			await interaction.response.send_message(f"Fehler beim Abrufen der Laufwerksinformationen: {str(e)}")

	@tree.command(
		name="netinfo",
		description="Zeigt Netzwerkinformationen",
		guild=discord.Object(id=server_id)
	)
	async def netinfo(interaction: Interaction):
		try:
			embed = Embed(title="🌐 Netzwerkinformationen", color=discord.Color.blue())
			
			net_if_addrs = psutil.net_if_addrs()
			net_io = psutil.net_io_counters()

			embed.add_field(
				name="Netzwerk I/O",
				value=f"```\nGesendet: {get_size(net_io.bytes_sent)}\n"
					  f"Empfangen: {get_size(net_io.bytes_recv)}```",
				inline=False
			)

			for interface_name, interface_addresses in net_if_addrs.items():
				for addr in interface_addresses:
					if str(addr.family) == 'AddressFamily.AF_INET':
						embed.add_field(
							name=f"Interface: {interface_name}",
							value=f"```\nIP: {addr.address}\nNetmask: {addr.netmask}```",
							inline=False
						)
			
			await interaction.response.send_message(embed=embed)
			
		except Exception as e:
			await interaction.response.send_message(f"Fehler beim Abrufen der Netzwerkinformationen: {str(e)}")