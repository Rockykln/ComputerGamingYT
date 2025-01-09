from source.client.config.imports import *
from source.client.config.client import client
from source.client.config.radio_stations import RADIO_STATIONS

radio_states = {}

def setup(tree: app_commands.CommandTree, server_id: str):
    
    async def play_radio(vc, url, volume):
        audio_source = FFmpegPCMAudio(url)
        transformed_source = PCMVolumeTransformer(audio_source, volume=volume)
        vc.play(transformed_source)

    @tree.command(
        name="radio",
        description="Spielt einen Radiosender ab",
        guild=discord.Object(id=server_id)
    )
    async def radio(interaction: discord.Interaction, station: str):
        if not interaction.user.voice:
            await interaction.response.send_message("Du musst in einem Sprachkanal sein!")
            return

        if station not in RADIO_STATIONS:
            stations_list = "\n".join(RADIO_STATIONS.keys())
            await interaction.response.send_message(f"Verfügbare Sender:\n{stations_list}")
            return

        voice_channel = interaction.user.voice.channel
        try:
            if interaction.guild.id not in radio_states:
                vc = await voice_channel.connect()
                radio_states[interaction.guild.id] = {"vc": vc, "volume": 1.0, "current_station": station}
            else:
                vc = radio_states[interaction.guild.id]["vc"]
                if vc.is_playing():
                    vc.stop()
                radio_states[interaction.guild.id]["current_station"] = station

            await play_radio(vc, RADIO_STATIONS[station], radio_states[interaction.guild.id]["volume"])
            await interaction.response.send_message(f"Spiele Radio: {station}")

        except Exception as e:
            await interaction.response.send_message(f"Fehler beim Abspielen: {str(e)}")

    @tree.command(
        name="radiovolume",
        description="Ändert die Radio-Lautstärke (0-200%)",
        guild=discord.Object(id=server_id)
    )
    async def radiovolume(interaction: discord.Interaction, level: int):
        if interaction.guild.id not in radio_states:
            await interaction.response.send_message("Ich spiele gerade kein Radio!")
            return
            
        if not 0 <= level <= 200:
            await interaction.response.send_message("Die Lautstärke muss zwischen 0 und 200 liegen!")
            return

        state = radio_states[interaction.guild.id]
        state["volume"] = level / 100

        if state["vc"].is_playing():
            state["vc"].stop()
            current_station = state["current_station"]
            await play_radio(state["vc"], RADIO_STATIONS[current_station], state["volume"])

        await interaction.response.send_message(f"Radio-Lautstärke auf {level}% gesetzt!")

    @tree.command(
        name="radiostop",
        description="Stoppt das Radio",
        guild=discord.Object(id=server_id)
    )
    async def radiostop(interaction: discord.Interaction):
        if interaction.guild.id not in radio_states:
            await interaction.response.send_message("Ich spiele gerade kein Radio!")
            return
        
        vc = radio_states[interaction.guild.id]["vc"]
        if vc.is_playing():
            vc.stop()
        await vc.disconnect()
        del radio_states[interaction.guild.id]
        await interaction.response.send_message("Radio gestoppt!")
