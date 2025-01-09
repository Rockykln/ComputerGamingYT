from typing import Dict, Any
from discord import VoiceClient

class VoiceState:
	def __init__(self):
		self.states: Dict[int, Dict[str, Any]] = {}

	def add_connection(self, guild_id: int, vc: VoiceClient, volume: float = 1.0):
		self.states[guild_id] = {"vc": vc, "volume": volume}

	def remove_connection(self, guild_id: int):
		if guild_id in self.states:
			del self.states[guild_id]

	def get_state(self, guild_id: int) -> Dict[str, Any]:
		return self.states.get(guild_id, {})

	def set_volume(self, guild_id: int, volume: float):
		if guild_id in self.states:
			self.states[guild_id]["volume"] = volume

voice_state = VoiceState()