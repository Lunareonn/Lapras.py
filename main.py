import discord
import os
import mariadb
import logging
import logging.handlers
import config
from dotenv import load_dotenv
from discord.ext import commands
from funcs import actions
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
    log.info(f"Ready. Logged in as {client.user}")


@client.event
async def on_guild_join(guild):
    actions.register_server(client.conn, guild.id)
    log.info(f"Bot was added to server {guild}")


@client.event
async def setup_hook():
    for cog in config.loaded_cogs:
        try:
            await client.load_extension(f"{cog}")
            log.info(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}:", e)
            log.exception(f"Failed to load cog {cog}:", e)


if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    conn = mariadb.connect(
        user=os.getenv("db_user"),
        password=os.getenv("db_pass"),
        host=os.getenv("db_host"),
        port=int(os.getenv("db_port")),
        database=os.getenv("db_name")
    )

    actions.setup_database(conn)
    client.conn = conn
    client.run(TOKEN, log_handler=None)
