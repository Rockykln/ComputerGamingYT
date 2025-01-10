import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
VOICE_CONFIG_FILE = os.path.join(DATA_DIR, 'voice_config.json')

default_config = {
	"join_channels": {}, 
	"temp_channels": {},  
}

def load_config():
	"""Load voice channel configuration from file"""
	os.makedirs(DATA_DIR, exist_ok=True)
	if os.path.exists(VOICE_CONFIG_FILE):
		with open(VOICE_CONFIG_FILE, 'r') as f:
			return json.load(f)
	return default_config

def save_config(config):
	"""Save voice channel configuration to file"""
	with open(VOICE_CONFIG_FILE, 'w') as f:
		json.dump(config, f, indent=4)

config = load_config()