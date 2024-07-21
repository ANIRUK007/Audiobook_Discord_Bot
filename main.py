import discord
from discord.ext import commands
import asyncio
import os
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store user progress
user_progress = {}

# Load user progress from file
def load_progress():
    global user_progress
    if os.path.exists('user_progress.json'):
        with open('user_progress.json', 'r') as f:
            user_progress = json.load(f)

# Save user progress to file
def save_progress():
    with open('user_progress.json', 'w') as f:
        json.dump(user_progress, f)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    load_progress()

@bot.command()
async def play(ctx, book_name: str):
    user_id = str(ctx.author.id)

    # Check if the book exists
    if not os.path.exists(f'audiobooks/{book_name}'):
        await ctx.send(f"Audiobook '{book_name}' not found.")
        return

    # Get the list of episodes
    episodes = sorted([ep for ep in os.listdir(f'audiobooks/{book_name}') if ep.endswith('01-Cosmos A Personal Voyage.mp3')])

    if not episodes:
        await ctx.send(f"No episodes found for '{book_name}'.")
        return

    # Get the user's progress
    if user_id not in user_progress:
        user_progress[user_id] = {}
    if book_name not in user_progress[user_id]:
        user_progress[user_id][book_name] = {'episode': 0, 'position': 0}

    current_episode = user_progress[user_id][book_name]['episode']
    position = user_progress[user_id][book_name]['position']

    # Connect to the user's voice channel
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    # Play episodes
    for i in range(current_episode, len(episodes)):
        episode = episodes[i]
        audio_source = discord.FFmpegPCMAudio(f'audiobooks/{book_name}/{episode}', options=f'-ss {position}')

        voice_client.play(audio_source)
        await ctx.send(f"Now playing: {book_name} - Episode {i+1}")

        # Wait for the audio to finish or be stopped
        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Update progress
        user_progress[user_id][book_name]['episode'] = i
        user_progress[user_id][book_name]['position'] = voice_client.source.get_position()
        save_progress()

        if not voice_client.is_connected():
            break

    if voice_client.is_connected():
        await voice_client.disconnect()
    await ctx.send(f"Finished playing '{book_name}'.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I'm not currently in a voice channel.")
        return

    await ctx.voice_client.disconnect()
    await ctx.send("Playback stopped and progress saved.")

bot.run("MTI2MjQwODI0MjA2MDA2NjgyNw.GObxsQ._Kb14tn0ngkqPybuAA9vtgrEIyvuGP9d2uksqo")