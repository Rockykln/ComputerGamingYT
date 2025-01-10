import platform
import subprocess
import re
import os

def get_gpu_info():
	"""Get GPU information across different platforms"""
	gpus = []
	system = platform.system()

	if system == "Windows":
		try:

			cmd = "powershell Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion"
			output = subprocess.check_output(cmd, shell=True).decode()
			

			for gpu in output.strip().split('\n')[2:]: 
				if gpu.strip():
					gpus.append({"name": gpu.strip()})
		except:
			gpus.append({"name": "GPU information unavailable"})

	elif system == "Linux":
		try:

			cmd = "lspci | grep -i 'vga\\|3d\\|2d'"
			output = subprocess.check_output(cmd, shell=True).decode()
			
			if output:
				for line in output.split('\n'):
					if line:

						gpu_name = line.split(':')[-1].strip()
						gpus.append({"name": gpu_name})

				try:
					nvidia_cmd = "nvidia-smi --query-gpu=gpu_name,memory.total,driver_version --format=csv,noheader"
					nvidia_output = subprocess.check_output(nvidia_cmd, shell=True).decode()
					if nvidia_output:
						gpus = []  
						for line in nvidia_output.split('\n'):
							if line:
								name, memory, driver = line.split(',')
								gpus.append({
									"name": name.strip(),
									"memory": memory.strip(),
									"driver": driver.strip()
								})
				except:
					pass
					
		except:
			gpus.append({"name": "GPU information unavailable"})
			
	elif system == "Darwin":  
		try:
			cmd = "system_profiler SPDisplaysDataType"
			output = subprocess.check_output(cmd, shell=True).decode()

			for line in output.split('\n'):
				if 'Chipset Model:' in line:
					gpu_name = line.split(':')[1].strip()
					gpus.append({"name": gpu_name})
		except:
			gpus.append({"name": "GPU information unavailable"})
			
	return gpus

def get_cpu_info():
	"""Get CPU information across different platforms"""
	system = platform.system()
	cpu_info = {
		"name": platform.processor(),
		"cores": os.cpu_count(),
		"architecture": platform.machine()
	}
	
	return cpu_info