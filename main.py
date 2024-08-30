import discord
import os
import sqlite3
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
    conn = sqlite3.connect("databases/database.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS \"{id}\" (cname TEXT, cvalue NULL);")
    conn.commit()
    print(f"bot was added to server {guild}")


@client.event
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename[:-3]}")

TOKEN = os.getenv("TOKEN")
client.run(TOKEN)
