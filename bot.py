#  R176 bot

from discord.ext import commands
from ossapi import Ossapi
import discord
import re

import os
from dotenv import load_dotenv
load_dotenv() 

# bs4
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ossapi
api = Ossapi(32365, os.getenv("OSU_API_KEY"))

# bs4
url = 'https://osu.ppy.sh/community/forums/55?sort=created#topics'
response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
else:
    print(f'Failed to retrieve the webpage. Status code: {response.status_code}')

@bot.event
async def on_ready():
    print("R176 activated")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("R176")

@bot.command()
async def add(ctx, *arr):
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result: {result}")

@bot.command()
async def top50(ctx):
    top50 = api.ranking("osu", "performance")
    results=[]
    for player in top50.ranking:
        results.append(player.user.username)
    await ctx.send(f"{results}")

@bot.command()
async def forum(ctx):
    topic = api.forum_topic(topic_id = 1927544, cursor_string = None, sort = None, limit = 2)
    await ctx.send(f"{topic.topic.title}")

# Prints out tournament forum post links that have "STD" or "std" in the title
@bot.command()
async def tournaments(ctx):
    links = soup.find_all('a', class_='u-ellipsis-overflow-desktop clickable-row-link forum-topic-entry__title')
    href_values = [a['href'] for a in links]
    posttitles = []
    for link in href_values:
        topic = api.forum_topic(topic_id = link[43:], cursor_string = None, sort = None, limit = 1)
        posttitles.append(topic.topic.title)
    pattern = re.compile(r"STD", re.IGNORECASE)
    stdindexs = [index for index, string in enumerate(posttitles) if re.search(pattern, string)]
    filterlinks = [href_values[i] for i in stdindexs]
    for link in filterlinks:
        await ctx.send(f"{link}")

bot.run(BOT_TOKEN)