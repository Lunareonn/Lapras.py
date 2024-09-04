import discord
import sqlite3
from typing import Optional
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect("databases/mod.db")

    @commands.has_permissions(ban_members=True, moderate_members=True)
    @commands.command()
    async def ban(self, ctx, user: Optional[discord.User], *, reason: str = ""):
        if user == ctx.author:
            return await ctx.send("You can't ban yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't ban myself!")

        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if user is not None and ctx.message.reference is not None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author

        dm_message = f"You have been banned from {ctx.guild}!"
        if reason:
            dm_message += f" Reason given: '{reason}'"
        try:
            await user.send(dm_message)
        except discord.HTTPException:
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

    @commands.has_permissions(ban_members=True, moderate_members=True)
    @commands.command()
    async def bandel(self, ctx, messagedel: int, user: Optional[discord.Member], *, reason: str = "Not specified"):
        if user == ctx.author:
            return await ctx.send("You can't ban yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't ban myself!")

        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if user is not None and ctx.message.reference is not None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author

        dm_message = f"You have been banned from {ctx.guild}!"
        if reason:
            dm_message += f" Reason given: '{reason}'"
        try:
            await user.send(dm_message)
        except discord.HTTPException:
            pass

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
            await ctx.send("Specified user couldn't be found.")
        if isinstance(error, discord.NotFound):
            await ctx.send("Specified user couldn't be found.")
        if isinstance(error, discord.Forbidden):
            await ctx.send("You don't have permissions to do that.")
        else:
            raise error

    @commands.has_permissions(ban_members=True, moderate_members=True)
    @commands.command()
    async def unban(self, ctx, user: discord.Member):
        await ctx.guild.unban(user)
        await ctx.send(f"{user} was unbanned! :thumbsup:")

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

    @commands.has_permissions(kick_members=True, moderate_members=True)
    @commands.command()
    async def kick(self, ctx, user: Optional[discord.Member], *, reason: str = ""):
        if user == ctx.author:
            return await ctx.send("You can't kick yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't kick myself!")

        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if user is not None and ctx.message.reference is not None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author

        dm_message = f"You were kicked from {ctx.guild}!"
        if reason:
            dm_message += f" Reason given: '{reason}'"
        dm_message += "\nYou can rejoin the server, but please behave this time."
        try:
            await user.send(dm_message)
        except discord.Forbidden:
            pass

        await user.kick(reason=reason)
        await ctx.send(f"{user} was kicked! :thumbsup:")

    # @commands.has_permissions(moderate_members=True)
    # @commands.command()
    # async def warn(self, ctx, user: Optional[discord.Member], *, reason: str = ""):
    #     cursor = self.conn.cursor()

    #     if user == ctx.author:
    #         return await ctx.send("You can't warn yourself!")
    #     elif user == self.client.user:
    #         return await ctx.send("I can't warn myself!")

    #     if user is None and ctx.message.reference is None:
    #         return await ctx.send("No user was specified!")
    #     else:
    #         if user is not None and ctx.message.reference is not None:
    #             message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    #             user = message.author


async def setup(client):
    await client.add_cog(Moderation(client))
