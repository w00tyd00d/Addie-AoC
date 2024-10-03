import asyncio
import datetime
import discord
import os

from aoc_scraper import Scraper
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

scraper = Scraper(datetime.date.today().year)

DEBUG_MODE = False
debug_channel_id = 556843112962457603

channel_id = 1167806493991645195 if not DEBUG_MODE else debug_channel_id
channel = None  # assigned at on_ready


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    global channel
    channel = client.get_channel(channel_id)
    if DEBUG_MODE:
        await send_message(channel, "Logged in!")
    await get_and_send_puzzle.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!test'):
        await send_message(channel, 'Test successful!')

    if message.content.startswith('!post'):
        await get_and_send_puzzle()


@tasks.loop(hours=24)
async def get_and_send_puzzle():
    day = str(datetime.date.today().day)
    for msg in scraper.get_day(day):
        await send_message(channel, msg)


@get_and_send_puzzle.before_loop
async def before_get_and_send_puzzle():
    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(now.date(), datetime.time(5, 2)) # 5:02am GMT
    if midnight < now:
        midnight += datetime.timedelta(days=1)

    seconds_until_midnight = (midnight - now).total_seconds()
    print("Minutes remaining:", seconds_until_midnight / 60)

    await asyncio.sleep(seconds_until_midnight)


async def send_message(channel, message):
    if channel:
        await channel.send(message)
    else:
        print("Unknown channel ID!")


if __name__ == "__main__":
    client.run(os.environ['DISCORD_TOKEN'])