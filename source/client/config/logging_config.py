from typing import Dict
import json
import os

LOGGING_CONFIG_FILE = 'logging_channels.json'

logging_channels: Dict[int, int] = {}

def load_logging_channels():
	"""Load logging channels from file"""
	global logging_channels
	try:
		if os.path.exists(LOGGING_CONFIG_FILE):
			with open(LOGGING_CONFIG_FILE, 'r') as f:
				
				data = json.load(f)
				logging_channels = {int(k): v for k, v in data.items()}
	except Exception as e:
		print(f"Error loading logging channels: {e}")
		logging_channels = {}

def save_logging_channel(guild_id: int, channel_id: int):
	"""Save the logging channel ID for a specific guild"""
	logging_channels[guild_id] = channel_id
	try:
		with open(LOGGING_CONFIG_FILE, 'w') as f:
			
			json.dump({str(k): v for k, v in logging_channels.items()}, f, indent=4)
	except Exception as e:
		print(f"Error saving logging channels: {e}")

def get_logging_channel(guild_id: int) -> int:
	"""Get the logging channel ID for a specific guild"""
	return logging_channels.get(guild_id)

load_logging_channels()