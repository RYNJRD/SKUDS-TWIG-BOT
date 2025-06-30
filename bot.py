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

# Load the last video ID from file, fallback to hardcoded if not present
last_video_id = load_last_video_id() or "x63FXbvvsNM"
intents = discord.Intents.default()

class MyBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(self.check_youtube)
