from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.performance_tracker import performance_tracker
from source.client.config.hardware_info import get_gpu_info, get_cpu_info

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
		description="Zeigt Hardware-Informationen",
		guild=discord.Object(id=server_id)
	)
	async def hardware(interaction: Interaction):
		await interaction.response.defer()
		
		cpu_info = get_cpu_info()
		cpu_usage = psutil.cpu_percent(interval=1)
		
		gpus = get_gpu_info()
		
		memory = psutil.virtual_memory()
		
		embed = Embed(title="💻 Hardware Informationen", color=discord.Color.blue())
		
		embed.add_field(
			name="CPU",
			value=f"```\nModell: {cpu_info['name']}\n"
				  f"Kerne: {cpu_info['cores']}\n"
				  f"Architektur: {cpu_info['architecture']}\n"
				  f"Auslastung: {cpu_usage}%```",
			inline=False
		)
		
		gpu_text = "```\n"
		for gpu in gpus:
			gpu_text += f"GPU: {gpu['name']}\n"
			if 'memory' in gpu:
				gpu_text += f"VRAM: {gpu['memory']}\n"
			if 'driver' in gpu:
				gpu_text += f"Treiber: {gpu['driver']}\n"
			gpu_text += "\n"
		gpu_text += "```"
		embed.add_field(name="GPU", value=gpu_text, inline=False)
		
		embed.add_field(
			name="RAM",
			value=f"```\nGesamt: {get_size(memory.total)}\n"
				  f"Verfügbar: {get_size(memory.available)}\n"
				  f"Auslastung: {memory.percent}%```",
			inline=False
		)
		
		await interaction.followup.send(embed=embed)



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