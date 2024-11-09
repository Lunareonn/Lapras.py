import discord
from typing import Optional
from discord.ext import commands
from funcs import actions


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn

    @commands.has_permissions(ban_members=True, moderate_members=True)
    @commands.command()
    async def ban(self, ctx, user: Optional[discord.User], *, reason: str = ""):
        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if ctx.message.reference is not None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author
        if user == ctx.author:
            return await ctx.send("You can't ban yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't ban myself!")

        dm_message = f"You have been banned from {ctx.guild}!"
        if reason:
            dm_message += f" Reason given: '{reason}'"
        try:
            await user.send(dm_message)
        except discord.HTTPException:
            pass

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)

        modlog_embed = discord.Embed(title="User was banned!", description=f"{user} was banned!")
        print(user.avatar.url)
        modlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=f"{user.avatar.url}")
        if reason:
            modlog_embed.add_field(name="Reason", value=f"{reason}", inline=True)
        modlog_embed.add_field(name="Issuer", value=f"{ctx.author}")
        await channel.send(embed=modlog_embed)

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
        server_id = ctx.guild.id
        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if ctx.message.reference is not None:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author
        if user == ctx.author:
            return await ctx.send("You can't ban yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't ban myself!")

        dm_message = f"You have been banned from {ctx.guild}!"
        if reason:
            dm_message += f" Reason given: '{reason}'"
        try:
            await user.send(dm_message)
        except discord.HTTPException:
            pass

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)

        modlog_embed = discord.Embed(title="User was banned!", description=f"{user} was banned!")
        modlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=f"{user.avatar.url}")
        if reason:
            modlog_embed.add_field(name="Reason", value=f"{reason}", inline=True)
        modlog_embed.add_field(name="Issuer", value=f"{ctx.author}")
        await channel.send(embed=modlog_embed)

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
        try:
            channel_id = actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)

        modlog_embed = discord.Embed(title="User was unbanned!", description=f"{user} was unbanned!")
        modlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=f"{user.avatar.url}")
        modlog_embed.add_field(name="Issuer", value=f"{ctx.author}")
        await channel.send(embed=modlog_embed)

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
        server_id = ctx.guild.id
        if user == ctx.author:
            return await ctx.send("You can't kick yourself!")
        elif user == self.client.user:
            return await ctx.send("I can't kick myself!")

        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if ctx.message.reference is not None:
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

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)

        modlog_embed = discord.Embed(title="User was kicked!", description=f"{user} was kicked!")
        modlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=f"{user.avatar.url}")
        modlog_embed.add_field(name="Issuer", value=f"{ctx.author}")
        await channel.send(embed=modlog_embed)

        await user.kick(reason=reason)
        await ctx.send(f"{user} was kicked! :thumbsup:")


async def setup(client):
    await client.add_cog(Moderation(client))
