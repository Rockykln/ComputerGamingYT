from source.client.config.imports import *
from source.client.config.client import client
from source.client.commands import radio, logging, system, voicechannels, tickets

tracemalloc.start()

load_dotenv()

token = os.getenv('TOKEN_SECRET')
server_id = os.getenv('CGYT_SERVER_ID')

tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():

    radio.setup(tree, server_id)
    logging.setup(tree, server_id)
    system.setup(tree, server_id)
    voice_handler = voicechannels.setup(tree, server_id)
    if voice_handler:
        client.event(voice_handler)
    tickets.setup(tree, server_id)
    
    await tree.sync(guild=discord.Object(id=server_id))
    print(f'Angemeldet als {client.user.name} (ID: {client.user.id})')


snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print(" [ Top 10 Speicherverbrauch ]")
for stat in top_stats[:10]:
    print(stat)

if __name__ == "__main__":
    client.run(token)