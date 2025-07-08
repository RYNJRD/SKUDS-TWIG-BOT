import discord
from discord.ext import commands
import feedparser
import asyncio
import os
import urllib.parse as urlparse

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_FEED_URL = os.getenv("YOUTUBE_FEED_URL")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

def save_last_video_id(video_id):
    with open("last_video_id.txt", "w") as f:
        f.write(video_id)

def load_last_video_id():
    if os.path.exists("last_video_id.txt"):
        with open("last_video_id.txt", "r") as f:
            return f.read().strip()
    return None

def extract_video_id(entry):
    # Try yt_videoid first
    video_id = getattr(entry, 'yt_videoid', None)
    if video_id:
        return video_id
    # Fallback: parse from URL
    video_url = entry.link
    parsed_url = urlparse.urlparse(video_url)
    return urlparse.parse_qs(parsed_url.query).get('v', [None])[0]

# Load last video ID from file or fallback to hardcoded
last_video_id = load_last_video_id() or "Ii_YhgiT-oM"

intents = discord.Intents.default()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.loop.create_task(self.check_youtube())
        await self.tree.sync()  # Sync slash commands on startup

    async def check_youtube(self):
        global last_video_id
        await self.wait_until_ready()
        channel = self.get_channel(DISCORD_CHANNEL_ID)

        while not self.is_closed():
            try:
                feed = feedparser.parse(YOUTUBE_FEED_URL)

                if feed.entries:
                    latest_video = feed.entries[0]
                    video_id = extract_video_id(latest_video)
                    video_url = latest_video.link
                    video_title = latest_video.title

                    if video_id and video_id != last_video_id:
                        last_video_id = video_id
                        save_last_video_id(video_id)
                        if channel:
                            await channel.send(f"📢 **New video uploaded!**\n**{video_title}**\n{video_url}")
                        else:
                            print("⚠️ Channel not found. Check DISCORD_CHANNEL_ID.")
                else:
                    print("⚠️ No videos found in RSS feed.")

            except Exception as e:
                print(f"Error checking YouTube feed: {e}")

            await asyncio.sleep(60)

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Bot is online! Logged in as {bot.user}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Watching YouTube")
    )

# Simple working slash command
@bot.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello!")

bot.run(DISCORD_TOKEN)
