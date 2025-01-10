import platform
import psutil
import subprocess
import os
import re

def get_size(bytes, suffix="B"):
	factor = 1024
	for unit in ["", "K", "M", "G", "T", "P"]:
		if bytes < factor:
			return f"{bytes:.2f}{unit}{suffix}"
		bytes /= factor

def get_cpu_info():
	cpu_info = {
		'physical_cores': psutil.cpu_count(logical=False),
		'total_cores': psutil.cpu_count(logical=True),
		'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else "N/A",
		'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
		'usage_per_core': [],
		'total_usage': psutil.cpu_percent(),
		'sockets': 1,  
		'model': platform.processor() or "N/A"
	}


	for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
		cpu_info['usage_per_core'].append(percentage)

	if platform.system() == "Linux":
		try:
			with open('/proc/cpuinfo', 'r') as f:
				cpuinfo = f.read()
			physical_ids = set(re.findall(r'physical id\s+:\s+(\d+)', cpuinfo))
			cpu_info['sockets'] = len(physical_ids) or 1
		except:
			pass

	return cpu_info

def get_memory_info():
	virtual_memory = psutil.virtual_memory()
	swap = psutil.swap_memory()
	
	return {
		'total': get_size(virtual_memory.total),
		'available': get_size(virtual_memory.available),
		'used': get_size(virtual_memory.used),
		'percentage': virtual_memory.percent,
		'swap_total': get_size(swap.total),
		'swap_used': get_size(swap.used),
		'swap_percentage': swap.percent
	}

def get_disk_info():
	disks = []
	for partition in psutil.disk_partitions():
		try:
			partition_usage = psutil.disk_usage(partition.mountpoint)
			disk_info = {
				'device': partition.device,
				'mountpoint': partition.mountpoint,
				'filesystem': partition.fstype,
				'total': get_size(partition_usage.total),
				'used': get_size(partition_usage.used),
				'free': get_size(partition_usage.free),
				'percentage': partition_usage.percent
			}
			disks.append(disk_info)
		except:
			continue
	return disks

def get_gpu_info():
	gpus = []
	
	if platform.system() == "Windows":
		try:
			
			import wmi
			w = wmi.WMI()
			for gpu in w.Win32_VideoController():
				gpus.append({
					'name': gpu.Name,
					'driver_version': gpu.DriverVersion,
					'memory': f"{round(int(gpu.AdapterRAM or 0) / (1024**3), 2)}GB" if gpu.AdapterRAM else "N/A"
				})
		except:
			pass
	elif platform.system() == "Linux":
		try:
	
			output = subprocess.check_output(['nvidia-smi', '--query-gpu=gpu_name,memory.total,driver_version', '--format=csv,noheader']).decode()
			for line in output.strip().split('\n'):
				name, memory, driver = line.split(',')
				gpus.append({
					'name': name.strip(),
					'memory': memory.strip(),
					'driver_version': driver.strip()
				})
		except:
			
			try:
				output = subprocess.check_output(['lspci', '-v'], universal_newlines=True)
				for line in output.split('\n'):
					if 'VGA' in line or '3D' in line:
						gpus.append({'name': line.split(':')[-1].strip()})
			except:
				pass
	
	return gpus

def get_motherboard_info():
	mobo_info = {
		'manufacturer': 'N/A',
		'model': 'N/A',
		'version': 'N/A',
		'serial': 'N/A'
	}
	
	if platform.system() == "Windows":
		try:
			import wmi
			w = wmi.WMI()
			board = w.Win32_BaseBoard()[0]
			mobo_info.update({
				'manufacturer': board.Manufacturer,
				'model': board.Product,
				'version': board.Version,
				'serial': board.SerialNumber
			})
		except:
			pass
	elif platform.system() == "Linux":
		try:
			with open('/sys/devices/virtual/dmi/id/board_vendor', 'r') as f:
				mobo_info['manufacturer'] = f.read().strip()
			with open('/sys/devices/virtual/dmi/id/board_name', 'r') as f:
				mobo_info['model'] = f.read().strip()
			with open('/sys/devices/virtual/dmi/id/board_version', 'r') as f:
				mobo_info['version'] = f.read().strip()
		except:
			pass
	
	return mobo_info