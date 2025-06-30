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

def extract_video_id(entry):
    # Try yt_videoid first
    video_id = getattr(entry, 'yt_videoid', None)
    if video_id:
        return video_id
    # Fallback: parse from URL
    video_url = entry.link
    parsed_url = urlparse.urlparse(video_url)
    return urlparse.parse_qs(parsed_url.query).get('v', [None])[0]

# Hardcode the last video ID here:
last_video_id = "0wHaTHdWp7c"
intents = discord.Intents.default()

class MyBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(self.check_youtube())

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

bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online! Logged in as {bot.user}")

    # Set presence to online with an activity
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Watching YouTube")
    )

bot.run(DISCORD_TOKEN)
