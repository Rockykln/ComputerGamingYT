from source.client.config.imports import *

async def custom_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": sys.platform,
                "$browser": "Discord Android",
                "$device": "Discord Android",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
            "v": 3,
        },
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "game": state._activity,
            "since": 0,
            "afk": False,
        }
    
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value

    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
    logging.info("Shard ID %s has sent the IDENTIFY payload.", self.shard_id)

DiscordWebSocket.identify = custom_identify

intents = discord.Intents.default()

intents.guilds = True
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.typing = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)