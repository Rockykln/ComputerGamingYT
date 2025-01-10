import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from source.client.bot import client, token

if __name__ == "__main__":
	client.run(token)
