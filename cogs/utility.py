import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_group()
    @commands.is_owner()
    async def presence(self, ctx):
        await ctx.send("Incorrect syntax! Try `presence set` or `presence clear`")

    @commands.is_owner()
    @presence.command()
    async def set(self, ctx, presence: str):
        await self.client.change_presence(activity=discord.Game(presence))
        await ctx.message.delete()
        await ctx.send(f"Done! Changed presence to `{presence}`")


async def setup(client):
    await client.add_cog(Utility(client))
