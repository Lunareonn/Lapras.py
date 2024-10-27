import discord
import os
import sqlite3
import config
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
intents = discord.Intents.all()
client = commands.AutoShardedBot(shard_count=1,
                                 command_prefix="$",
                                 intents=intents)


@client.command()
@commands.is_owner()
async def test(ctx: commands.Context):
    shard_id = ctx.guild.shard_id
    await ctx.send(f"shit works on shard {shard_id}")


@client.event
async def on_ready():
    print(f"Ready. Logged in as {client.user}")


@client.event
async def on_guild_join(guild):
    id = str(guild.id)
    conn = sqlite3.connect("databases/config.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS \"{id}\" (cname TEXT, cvalue NULL);")
    conn.commit()

    conn = sqlite3.connect("databases/macros.db")
    conn.exeucte(f"CREATE TABLE IF NOT EXISTS \"{id}\" (name TEXT, alias TEXT, content TEXT)")
    conn.commit()

    conn = sqlite3.connect("databases/mod.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS \"{id}\" (userid INTEGER, username TEXT, issuer INTEGER, reason TEXT, count INTEGER, timestamp BLOB)")
    conn.commit()
    print(f"bot was added to server {guild}")


@client.event
async def setup_hook():
    for cog in config.loaded_cogs:
        try:
            await client.load_extension(f"{cog}")
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}:", e)

TOKEN = os.getenv("TOKEN")
client.run(TOKEN)
