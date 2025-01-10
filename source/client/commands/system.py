from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.performance_tracker import performance_tracker
import wmi
import GPUtil

def get_size(bytes, suffix="B"):
	factor = 1024
	for unit in ["", "K", "M", "G", "T", "P"]:
		if bytes < factor:
			return f"{bytes:.2f}{unit}{suffix}"
		bytes /= factor

def setup(tree: app_commands.CommandTree, server_id: str):

	performance_tracker.start()
	
	@tree.command(
		name="performance",
		description="Zeigt Performance-Statistiken der letzten Stunden",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def performance(interaction: Interaction, hours: int = 2):
		await interaction.response.defer()
		
		metrics = performance_tracker.get_metrics(hours)
		
		cpu_avg = sum(v for _, v in metrics['cpu']) / len(metrics['cpu']) if metrics['cpu'] else 0
		mem_avg = sum(v for _, v in metrics['memory']) / len(metrics['memory']) if metrics['memory'] else 0
		disk_avg = sum(v for _, v in metrics['disk']) / len(metrics['disk']) if metrics['disk'] else 0
		
		embed = Embed(title="📊 Performance Übersicht", color=discord.Color.blue())
		embed.add_field(
			name="CPU Auslastung",
			value=f"Durchschnitt: {cpu_avg:.1f}%\n"
				  f"Aktuell: {psutil.cpu_percent()}%",
			inline=False
		)
		embed.add_field(
			name="RAM Auslastung",
			value=f"Durchschnitt: {mem_avg:.1f}%\n"
				  f"Aktuell: {psutil.virtual_memory().percent}%",
			inline=False
		)
		embed.add_field(
			name="Festplatten Auslastung",
			value=f"Durchschnitt: {disk_avg:.1f}%\n"
				  f"Aktuell: {psutil.disk_usage('/').percent}%",
			inline=False
		)
		
		await interaction.followup.send(embed=embed)

	@tree.command(
		name="processes",
		description="Zeigt die Top-Prozesse nach CPU-Auslastung",
		guild=discord.Object(id=server_id)
	)
	@app_commands.checks.has_permissions(administrator=True)
	async def processes(interaction: Interaction):
		processes = []
		for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
			try:
				processes.append(proc.info)
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				pass
		
		processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
		
		embed = Embed(title="🔄 Top Prozesse", color=discord.Color.blue())
		process_text = ""
		for proc in processes[:10]: 
			process_text += f"**{proc['name']}** (PID: {proc['pid']})\n"
			process_text += f"CPU: {proc['cpu_percent']}% | RAM: {proc['memory_percent']:.1f}%\n\n"
		
		embed.description = process_text
		await interaction.response.send_message(embed=embed)

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
			w = wmi.WMI()
			embed = Embed(title="💻 Hardware Informationen", color=discord.Color.blue())
			
			cpu_info = w.Win32_Processor()[0]
			embed.add_field(
				name="CPU",
				value=f"```\nModell: {cpu_info.Name}\n"
					  f"Kerne: {cpu_info.NumberOfCores}\n"
					  f"Threads: {cpu_info.NumberOfLogicalProcessors}\n"
					  f"Basis Takt: {cpu_info.MaxClockSpeed}MHz```",
				inline=False
			)
			
			ram = psutil.virtual_memory()
			ram_slots = w.Win32_PhysicalMemory()
			ram_info = "```\n"
			ram_info += f"Gesamt: {get_size(ram.total)}\n"
			for slot in ram_slots:
				ram_info += f"Slot: {get_size(int(slot.Capacity))} "
				ram_info += f"({slot.Speed}MHz)\n"
			ram_info += "```"
			embed.add_field(name="RAM", value=ram_info, inline=False)
			
			try:
				gpus = GPUtil.getGPUs()
				if gpus:
					gpu_info = "```\n"
					for gpu in gpus:
						gpu_info += f"Modell: {gpu.name}\n"
						gpu_info += f"VRAM: {gpu.memoryTotal}MB\n"
						gpu_info += f"Last: {gpu.load*100:.1f}%\n"
					gpu_info += "```"
					embed.add_field(name="GPU", value=gpu_info, inline=False)
			except:
				pass  
			
			disk_info = "```\n"
			for disk in w.Win32_DiskDrive():
				size = int(disk.Size or 0)
				disk_info += f"Laufwerk: {disk.Model}\n"
				if size > 0:
					disk_info += f"Größe: {get_size(size)}\n"
			disk_info += "```"
			embed.add_field(name="Festplatten", value=disk_info, inline=False)
			
			board = w.Win32_BaseBoard()[0]
			embed.add_field(
				name="Motherboard",
				value=f"```\nHersteller: {board.Manufacturer}\n"
					  f"Modell: {board.Product}```",
				inline=False
			)
			
			await interaction.followup.send(embed=embed)
			
		except Exception as e:
			print(f"Hardware info error: {str(e)}")
			await interaction.followup.send("Fehler beim Abrufen der Hardware-Informationen.")

	@tree.command(
		name="uptime",
		description="Zeigt System- und Bot-Uptime",
		guild=discord.Object(id=server_id)
	)
	async def uptime(interaction: Interaction):
		boot_time = datetime.fromtimestamp(psutil.boot_time())
		uptime = datetime.now() - boot_time
		
		embed = Embed(title="⏰ Uptime Information", color=discord.Color.blue())
		embed.add_field(
			name="System Uptime",
			value=f"{uptime.days} Tage, {uptime.seconds//3600} Stunden, "
				  f"{(uptime.seconds//60)%60} Minuten",
			inline=False
		)
		
		await interaction.response.send_message(embed=embed)