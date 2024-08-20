import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, user: discord.Member, reason: str):
        await user.ban(delete_message_seconds=0, reason=reason)
        await ctx.send(f"{user} has been banned! :thumbsup:")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")
        if isinstance(error, discord.NotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.Forbidden):
            await ctx.send("You can't do that.")
        if isinstance(error, discord.HTTPException):
            await ctx.send(f"**discord.HTTPException raised! Something went wrong. Ping @lunareonn if issue persists.\n{error}")


async def setup(client):
    await client.add_cog(Moderation(client))
