from source.client.config.imports import *
from source.client.config.client import client
import asyncio
from source.client.config.hardware_info import (
	get_cpu_info, get_memory_info, get_disk_info,
	get_gpu_info, get_motherboard_info
)


def get_size(bytes, suffix="B"):
	factor = 1024
	for unit in ["", "K", "M", "G", "T", "P"]:
		if bytes < factor:
			return f"{bytes:.2f}{unit}{suffix}"
		bytes /= factor




def setup(tree: app_commands.CommandTree, server_id: str):


	@tree.command(
		name="processes",
		description="Zeigt die Top-Prozesse nach CPU-Auslastung",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def processes(interaction: Interaction):
		await interaction.response.defer()
		
		processes = []
		for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'status']):
			try:
				proc.cpu_percent()  
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				pass

		await asyncio.sleep(1)
		
		for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'status']):
			try:
				info = proc.info
				processes.append(info)
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				pass
		
		
		processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
		
		embed = Embed(title="🔄 Top Prozesse", color=discord.Color.blue())
		process_text = ""
		for proc in processes[:40]:  
			process_text += f"**{proc['name']}** (PID: {proc['pid']})\n"
			process_text += f"CPU: {proc['cpu_percent']:.1f}% | RAM: {proc['memory_percent']:.1f}%\n"
			process_text += f"Status: {proc['status']}\n\n"
		
		embed.description = process_text
		await interaction.followup.send(embed=embed)




	@tree.command(
		name="services",
		description="Zeigt laufende System-Services",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def services(interaction: Interaction):
		await interaction.response.defer()
		
		services_list = []
		for service in psutil.win_service_iter():
			try:
				info = service.as_dict()
				if info['status'] == 'running':
					services_list.append(info)
			except:
				continue
		
		embed = Embed(title="🔧 Laufende System-Services", color=discord.Color.blue())
		services_text = ""
		for service in services_list[:15]:  
			services_text += f"**{service['name']}**\n"
			services_text += f"Display Name: {service['display_name']}\n"
			services_text += f"Status: {service['status']}\n\n"
		
		embed.description = services_text
		await interaction.followup.send(embed=embed)

	@tree.command(
		name="systemload",
		description="Zeigt detaillierte System-Auslastung",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def systemload(interaction: Interaction):
		await interaction.response.defer()

		cpu_freq = psutil.cpu_freq(percpu=True)
		cpu_percent = psutil.cpu_percent(percpu=True)
		
		embed = Embed(title="📊 System-Auslastung", color=discord.Color.blue())
		
		cpu_text = "```\n"
		for i, (freq, percent) in enumerate(zip(cpu_freq, cpu_percent)):
			cpu_text += f"Core {i}: {percent}% @ {freq.current:.0f}MHz\n"
		cpu_text += "```"
		embed.add_field(name="CPU Auslastung pro Kern", value=cpu_text, inline=False)

		memory = psutil.virtual_memory()
		swap = psutil.swap_memory()
		mem_text = f"```\nRAM Gesamt: {get_size(memory.total)}\n"
		mem_text += f"RAM Verfügbar: {get_size(memory.available)}\n"
		mem_text += f"RAM Genutzt: {memory.percent}%\n"
		mem_text += f"Swap Genutzt: {swap.percent}%```"
		embed.add_field(name="Speicher-Auslastung", value=mem_text, inline=False)
		
		
		net_io = psutil.net_io_counters()
		net_text = f"```\nGesendet: {get_size(net_io.bytes_sent)}\n"
		net_text += f"Empfangen: {get_size(net_io.bytes_recv)}\n"
		net_text += f"Pakete Gesendet: {net_io.packets_sent}\n"
		net_text += f"Pakete Empfangen: {net_io.packets_recv}```"
		embed.add_field(name="Netzwerk-Statistiken", value=net_text, inline=False)
		
		await interaction.followup.send(embed=embed)

	@tree.command(
		name="network",
		description="Zeigt Netzwerk-Statistiken",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def network(interaction: Interaction):
		net_io = psutil.net_io_counters()
		
		embed = Embed(title="🌐 Netzwerk Statistiken", color=discord.Color.blue())
		embed.add_field(
			name="Gesendet",
			value=get_size(net_io.bytes_sent),
			inline=True
		)
		embed.add_field(
			name="Empfangen",
			value=get_size(net_io.bytes_recv),
			inline=True
		)
		embed.add_field(
			name="Pakete",
			value=f"Gesendet: {net_io.packets_sent}\nEmpfangen: {net_io.packets_recv}",
			inline=False
		)
		
		await interaction.response.send_message(embed=embed)

	@tree.command(
		name="hardware",
		description="Zeigt detaillierte Hardware-Informationen",
		guild=discord.Object(id=server_id)
	)
	async def hardware(interaction: Interaction):
		await interaction.response.defer()
		
		try:

			cpu_info = get_cpu_info()
			memory_info = get_memory_info()
			disk_info = get_disk_info()
			gpu_info = get_gpu_info()
			mobo_info = get_motherboard_info()

			embed = Embed(title="💻 Hardware Informationen", color=discord.Color.blue())
	
			cpu_text = f"```\nModell: {cpu_info['model']}\n"
			cpu_text += f"Physische Sockel: {cpu_info['sockets']}\n"
			cpu_text += f"Physische Kerne: {cpu_info['physical_cores']}\n"
			cpu_text += f"Logische Kerne: {cpu_info['total_cores']}\n"
			cpu_text += f"Maximale Frequenz: {cpu_info['max_frequency']}MHz\n"
			cpu_text += f"Aktuelle Frequenz: {cpu_info['current_frequency']}MHz\n"
			cpu_text += f"Gesamtauslastung: {cpu_info['total_usage']}%```"
			embed.add_field(name="CPU", value=cpu_text, inline=False)

			ram_text = f"```\nGesamt: {memory_info['total']}\n"
			ram_text += f"Verfügbar: {memory_info['available']}\n"
			ram_text += f"Verwendet: {memory_info['used']}\n"
			ram_text += f"Auslastung: {memory_info['percentage']}%\n"
			ram_text += f"Swap Gesamt: {memory_info['swap_total']}\n"
			ram_text += f"Swap Verwendet: {memory_info['swap_used']} ({memory_info['swap_percentage']}%)```"
			embed.add_field(name="RAM", value=ram_text, inline=False)
			
			if gpu_info:
				gpu_text = "```\n"
				for i, gpu in enumerate(gpu_info, 1):
					gpu_text += f"GPU {i}:\n"
					gpu_text += f"Name: {gpu.get('name', 'N/A')}\n"
					if 'memory' in gpu:
						gpu_text += f"Speicher: {gpu['memory']}\n"
					if 'driver_version' in gpu:
						gpu_text += f"Treiber: {gpu['driver_version']}\n"
					gpu_text += "\n"
				gpu_text += "```"
				embed.add_field(name="GPU(s)", value=gpu_text, inline=False)
			
		
			mobo_text = f"```\nHersteller: {mobo_info['manufacturer']}\n"
			mobo_text += f"Modell: {mobo_info['model']}\n"
			mobo_text += f"Version: {mobo_info['version']}```"
			embed.add_field(name="Motherboard", value=mobo_text, inline=False)
			
			
			disk_text = "```\n"
			for disk in disk_info:
				disk_text += f"Laufwerk: {disk['device']}\n"
				disk_text += f"Dateisystem: {disk['filesystem']}\n"
				disk_text += f"Größe: {disk['total']}\n"
				disk_text += f"Verwendet: {disk['used']} ({disk['percentage']}%)\n"
				disk_text += f"Frei: {disk['free']}\n\n"
			disk_text += "```"
			embed.add_field(name="Festplatten", value=disk_text, inline=False)
			
			await interaction.followup.send(embed=embed)
			
		except Exception as e:
			print(f"Hardware info error: {str(e)}")
			await interaction.followup.send("Fehler beim Abrufen der Hardware-Informationen.")
