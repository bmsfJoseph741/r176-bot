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
url = 'https://osu.ppy.sh/community/forums/55?sort=created#topics' # tournament forum first page url
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

# Prints out tournament forum post links that have "STD" or "std" in the title (front page)
@bot.command()
async def tournaments(ctx):
    links = soup.find_all('a', class_='u-ellipsis-overflow-desktop clickable-row-link forum-topic-entry__title') # parses <a href> tags
    href_values = [a['href'] for a in links] # finds all <a href> values (links)
    posttitles = [] # store post titles
    for link in href_values: 
        topic = api.forum_topic(topic_id = link[43:], cursor_string = None, sort = None, limit = 1)
        posttitles.append(topic.topic.title)
    pattern = re.compile(r"STD", re.IGNORECASE)
    stdindexs = [index for index, string in enumerate(posttitles) if re.search(pattern, string)]
    filterlinks = [href_values[i] for i in stdindexs]
    for link in filterlinks:
        await ctx.send(f"{link}")

# Prints a tournament
@bot.command()
async def big_data(ctx, link: str):
    digits = [d for d in link if d.isdigit()]

    if len(digits) > 7:
        topic_id = ''.join(digits[:-1])
    else:
        topic_id = ''.join(digits)

    forum = api.forum_topic(topic_id)
    html = forum.posts[0].body.html
    links = ""
    discordlink = re.findall(r'https://(?:www\.)?discord\.gg/[0-9a-zA-Z]+', html)
    challongelink = re.findall(r'https://(?:www\.)?challonge\.com/[0-9a-zA-Z]+', html)
    twitchlink = re.findall(r'https://(?:www\.)?twitch\.tv/[0-9a-zA-Z_-]+', html)
    sheetlink = re.findall(r'https://(?:www\.)?docs\.google\.com/spreadsheets/d/[0-9a-zA-Z_-]+', html)
    formlink = re.findall(r'https://(?:www\.)?docs\.google\.com/forms/d/e/[0-9a-zA-Z_-]+/viewform', html)

    # Print Forum Topic/Title
    links += f"# {forum.topic.title}\n"

    # Print Forum Post Link
    links += f'**Forum Post:**\n<https://osu.ppy.sh/community/forums/topics/{topic_id}>\n'

    # Print Google Sheets link(s)
    if sheetlink:
        sheetlinks = ""
        for link in sheetlink:
            sheetlinks += f"<{link}>\n"
        links += f"**Sheets:** \n{sheetlinks}"
    else:
        links += "**Sheets:** \n__None provided.__\n"

    # Print Discord link
    if discordlink:
        links += f"**Discord:**\n{discordlink.pop(0)}\n"
    else:
        links += "**Discord:** \n__None provided.__\n"

    # Print Twitch link(s)
    if twitchlink:
        twitchlinks = ""
        
        for link in twitchlink:
            twitchlinks += f"<{link}>\n"
        links += f"**Twitch:** \n{twitchlinks}"
    else:
        links += "**Twitch:** \n__None provided.__\n"

    # Print Challonge link
    if challongelink:
        challongelinks = ""
        
        for link in challongelink:
            challongelinks += f"<{link}>\n"
        links += f"**Challonge:** \n{challongelinks}"
    else:
        links += "**Challonge:** \n__None provided.__\n"

    if formlink:
        formlinks = ""
        for link in formlink:
            formlinks += f"<{link}>\n"
        links += f"**Registrations:** \n{formlinks}"
    else:
        formlink = re.findall(r'https://forms\.gle/[0-9a-zA-Z_]+', html)
        if formlink:
            formlinks = ""
            for link in formlink:
                formlinks += f"<{link}>\n"
            links += f"**Registrations:** \n{formlinks}"
        else: 
            links += "**Registrations:** \n__None provided.__\n"

    await ctx.send(f"{links}")

@bot.command()
async def discord_link(ctx):
    forum = api.forum_topic(topic_id = 1927544)
    html = forum.posts[0].body.html

    discordlink = re.findall(r'https://discord\.gg/[0-9a-zA-Z]+', html)
    if discordlink:
        await ctx.send(f"{discordlink.pop(0)}")
    else:
        await ctx.send(f"No discord provided.")

@bot.command()
async def challonge(ctx):
    forum = api.forum_topic(topic_id = 1927544)
    html = forum.posts[0].body.html

    challongelink = re.findall(r'https://challonge\.com/[0-9a-zA-Z_-]+', html)
    if challongelink:
        await ctx.send(f"{challongelink.pop(0)}")
    else:
        await ctx.send(f"No challonge provided.")

@bot.command()
async def stream(ctx):
    forum = api.forum_topic(topic_id = 1927544)
    html = forum.posts[0].body.html

    twitchlink = re.findall(r'https://twitch\.tv/[0-9a-zA-Z_-]+', html)
    if twitchlink:
        links = ""
        for link in twitchlink:
            links += link + "\n"
        await ctx.send(f"{links}")   
    else:
        await ctx.send(f"No twitch provided.")

@bot.command()
async def sheet(ctx):
    forum = api.forum_topic(topic_id = 1927544)
    html = forum.posts[0].body.html

    sheetlink = re.findall(r'https://docs\.google\.com/spreadsheets/d/[0-9a-zA-Z_-]+', html)
    if sheetlink:
        await ctx.send(f"{sheetlink}")
    else:
        await ctx.send(f"No sheet provided.") 

@bot.command()
async def registrations(ctx):
    forum = api.forum_topic(topic_id = 1954778)
    html = forum.posts[0].body.html

    formlink = re.findall(r'https://docs\.google\.com/forms/d/e/[0-9a-zA-Z_-]+/viewform', html)

    if formlink:
        links = ""
        for link in formlink:
            links += link + "\n"
        await ctx.send(f"{links}")  
    else:
        formlink = re.findall(r'https://forms\.gle/[0-9a-zA-Z_-]+', html)
        if formlink:
            links = ""
            for link in formlink:
                links += link + "\n"
            await ctx.send(f"{links}")
        else: 
            await ctx.send(f"No sheet provided.") 

bot.run(BOT_TOKEN)