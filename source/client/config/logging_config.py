from typing import Dict

logging_channels: Dict[int, int] = {}

def save_logging_channel(guild_id: int, channel_id: int):
	"""Save the logging channel ID for a specific guild"""
	logging_channels[guild_id] = channel_id

def get_logging_channel(guild_id: int) -> int:
	"""Get the logging channel ID for a specific guild"""
	return logging_channels.get(guild_id)