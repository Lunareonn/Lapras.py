import discord
import os
import sqlite3
import logging
import logging.handlers
import config
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
intents = discord.Intents.all()
client = commands.AutoShardedBot(shard_count=1,
                                 command_prefix="$",
                                 intents=intents)

log = logging.getLogger('discord')
log.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=64 * 1024 * 1024,
    backupCount=5
)
dt_frmt = "%d-%m-%Y %H:%M:%S"
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_frmt, style="{")
handler.setFormatter(formatter)
log.addHandler(handler)
client.log = log


@client.event
async def on_ready():
    print(f"Ready. Logged in as {client.user}")


@client.event
async def on_guild_join(guild):
    server_id = str(guild.id)
    conn = sqlite3.connect("databases/config.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS \"{server_id}\" (cname TEXT, cvalue NULL);")
    conn.commit()

    conn = sqlite3.connect("databases/macros.db")
    conn.exeucte(f"CREATE TABLE IF NOT EXISTS \"{server_id}\" (name TEXT, alias TEXT, content TEXT)")
    conn.commit()

    conn = sqlite3.connect("databases/mod.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS \"{server_id}\" (userid INTEGER, username TEXT, issuer INTEGER, reason TEXT, count INTEGER, timestamp BLOB)")
    conn.commit()
    print(f"bot was added to server {guild}")


@client.event
async def setup_hook():
    for cog in config.loaded_cogs:
        try:
            await client.load_extension(f"{cog}")
            print(f"Loaded cog: {cog}")
            log.info(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}:", e)
            log.exception(f"Failed to load cog {cog}:", e)

TOKEN = os.getenv("TOKEN")
client.run(TOKEN, log_handler=None)
