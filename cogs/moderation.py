import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, user: discord.User, reason: str):
        try:
            dm_embed = discord.Embed(title=f"You have been banned from {ctx.guild.name}",
                                     description=f"Reason: {reason}",
                                     colour=0xf43100)
            await user.send(embed=dm_embed)
        except discord.HTTPException:
            print(f"Couldn't send a Direct Message to {user.id}")
            pass

        await ctx.guild.ban(user, delete_message_seconds=0, reason=reason)
        await ctx.send(f"{user} has been banned! :thumbsup:")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await ctx.message.delete()
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")
            except discord.Forbidden:
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}\n**WARNING!** ``discord.Forbidden`` was raised! I may be missing important permissions.")
        if isinstance(error, commands.UserNotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.NotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.Forbidden):
            await ctx.send("You don't have permissions to do that.")
        else:
            raise error

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def bandel(self, ctx, user: discord.Member, reason: str, messagedel: int):
        dm_embed = discord.Embed(title="You have been banned from {}",
                                 description="Reason: {}",
                                 colour=0xf43100)
        await user.send(dm_embed)

        await ctx.guild.ban(user, delete_message_days=messagedel, reason=reason)
        await ctx.send(f"{user} has been banned! :thumbsup:")

    @bandel.error
    async def bandel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await ctx.message.delete()
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")
            except discord.Forbidden:
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}\n**WARNING!** ``discord.Forbidden`` was raised! I may be missing important permissions.")
        if isinstance(error, commands.UserNotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.NotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.Forbidden):
            await ctx.send("You don't have permissions to do that.")
        else:
            raise error

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, user: discord.Member):
        await user.unban()
        await ctx.send(f"{user} has been unbanned! :thumbsup:")

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await ctx.message.delete()
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")
            except discord.Forbidden:
                await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}\n**WARNING!** ``discord.Forbidden`` was raised! I may be missing important permissions.")
        if isinstance(error, commands.UserNotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.NotFound):
            await ctx.send("Given user was not found!")
        if isinstance(error, discord.Forbidden):
            await ctx.send("You don't have permissions to do that.")
        else:
            raise error


async def setup(client):
    await client.add_cog(Moderation(client))
