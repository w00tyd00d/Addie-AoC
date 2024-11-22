import asyncio
import datetime
import discord
import json
import os

from aoc_scraper import Scraper
from discord.ext import tasks, commands

class Struct:
    def __init__(self, data):
        self.__dict__.update(data)

with open(os.path.join(os.path.dirname(__file__), "settings.json")) as f:
    settings = Struct(json.loads(f.read()))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!aoc ", intents=intents)
scraper = Scraper(datetime.date.today().year)

guild = None # assigned at on_ready
aoc_channel = None  # assigned at on_ready


def save_settings():
    with open(os.path.join(os.path.dirname(__file__), "settings.json"), "w") as f:
        f.write(json.dumps(settings.__dict__, indent=4))


def get_member(id: int) -> discord.Member:
    return guild.get_member(int(id))


def set_aoc_channel(cid: int):
    global aoc_channel
    aoc_channel = bot.get_channel(cid)


async def send_message(channel: discord.GroupChannel, msg: str, embed: discord.Embed = None):
    if channel is None:
        print("Error: Channel does not exist.")
        return
    await channel.send(msg, embed=embed)


async def send_direct_message(user: discord.Member, msg: str, embed: discord.Embed = None):
    await user.create_dm()
    await send_message(user.dm_channel, msg, embed=embed)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    
    global guild
    guild_id = settings.debug_guild_id if settings.debug_mode else settings.guild_id
    guild = bot.get_guild(guild_id)
    
    set_aoc_channel(settings.aoc_channel_id)
    if settings.debug_mode:
        user = get_member(settings.debug_user_id)
        await send_direct_message(user, "Logged in!")
    
    await get_and_send_puzzle.start()


@bot.command
async def test(ctx):
    await send_message(aoc_channel, "Test successful!")


@bot.command(aliases=["reg", "register", "set"])
async def register_channel(ctx):
    cid = ctx.channel.id
    settings.aoc_channel_id = cid

    save_settings()
    set_aoc_channel(cid)

    await send_message(aoc_channel, "New channel set!")


@bot.command(name="post")
async def post_current_day_puzzle(ctx, force_scrape: str = "false"):
    today = datetime.date.today()
    if today.month != 12 or today.day > 25:
        await send_message(aoc_channel, "No puzzle today!")
        return
    
    force_scrape = True if force_scrape.lower() == "true" else False
    await get_and_send_puzzle(force_scrape)


@tasks.loop(hours=24)
async def get_and_send_puzzle(day: int = None, force_scrape = False):
    today = datetime.date.today()
    if today.month != 12 or today.day > 25:
        return

    for msg in scraper.get_puzzle(today.day, force_scrape):
        await send_message(aoc_channel, msg)


@get_and_send_puzzle.before_loop
async def before_get_and_send_puzzle():
    now = datetime.datetime.now()
    
    midnight = datetime.datetime.combine(now.date(), datetime.time(5, 2)) # 5:02am GMT
    if midnight < now:
        midnight += datetime.timedelta(days=1)

    seconds_until_midnight = (midnight - now).total_seconds()
    print("Minutes remaining to midnight:", seconds_until_midnight / 60)

    await asyncio.sleep(seconds_until_midnight)


if __name__ == "__main__":
    bot.run(settings.discord_token)