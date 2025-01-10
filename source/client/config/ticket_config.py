import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TICKET_CONFIG_FILE = os.path.join(DATA_DIR, 'ticket_config.json')

default_config = {
	"ticket_channels": {},  
	"support_categories": {},  
	"active_tickets": {},  
	"ticket_counter": {}  
}

def load_config():
	"""Load ticket configuration from file"""
	os.makedirs(DATA_DIR, exist_ok=True)
	if os.path.exists(TICKET_CONFIG_FILE):
		with open(TICKET_CONFIG_FILE, 'r') as f:
			return json.load(f)
	return default_config

def save_config(config):
	"""Save ticket configuration to file"""
	with open(TICKET_CONFIG_FILE, 'w') as f:
		json.dump(config, f, indent=4)

config = load_config()