import discord
from typing import Optional
from discord.ext import commands
from funcs import actions


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.pconn = client.pconn

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.pconn, ctx.guild.id, "moderation")
        if selected_cog:
            return False
        return True

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: Optional[discord.User], *, reason: str = ""):
        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if ctx.message.reference:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author

        if user == ctx.author:
            return await ctx.send("You can't ban yourself!")
        if user == self.client.user:
            return await ctx.send("I can't ban myself!")

        direct_message = f"You have been banned from {ctx.guild}"
        if reason:
            direct_message += f"\nReason given: {reason}"

        await ctx.guild.ban(user, delete_message_seconds=0, reason=reason)
        await ctx.send(f"{user} has been banned! :thumbsup:")
        actions.add_mod_record(self.client.conn, ctx.guild.id, ctx.author.id, user.id, reason, None, "ban")

        try:
            await user.send(direct_message)
        except discord.HTTPException:
            pass

        try:
            actionlogs_channel = await self.client.fetch_channel(actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id))
        except TypeError:
            return

        actionlog_embed = discord.Embed(title="User was banned!", description=f"{user} has been banned.")
        actionlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=user.avatar.url)
        if reason:
            actionlog_embed.add_field(name="Reason:", value=reason, inline=True)
        actionlog_embed.add_field(name="Issuer:", value=ctx.author)
        await actionlogs_channel.send(embed=actionlog_embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: Optional[discord.User], *, reason: str = ""):
        if user is None and ctx.message.reference is None:
            return await ctx.send("No user was specified!")
        else:
            if ctx.message.reference:
                message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                user = message.author

        if user == ctx.author:
            return await ctx.send("You can't kick yourself!")
        if user == self.client.user:
            return await ctx.send("I can't kick myself!")

        direct_message = f"You have been kicked from {ctx.guild}"
        if reason:
            direct_message += f"Reason: {reason}"
        direct_message += "\nYou can rejoin, but please behave this time."

        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"{user} has been banned! :thumbsup:")
        actions.add_mod_record(self.client.conn, ctx.guild.id, ctx.author.id, user.id, reason, None, "kick")

        try:
            await user.send(direct_message)
        except discord.HTTPException:
            pass

        try:
            actionlogs_channel = await self.client.fetch_channel(actions.fetch_actionlog_channel(self.client.conn, ctx.guild.id))
        except TypeError:
            return

        actionlog_embed = discord.Embed(title="User was kicked!", description=f"{user} has been kicked.")
        actionlog_embed.set_author(name=f"{user.display_name} ({user})", icon_url=user.avatar.url)
        if reason:
            actionlog_embed.add_field(name="Reason:", value=reason, inline=True)
        actionlog_embed.add_field(name="Issuer:", value=ctx.author)
        await actionlogs_channel.send(embed=actionlog_embed)


async def setup(client):
    await client.add_cog(Moderation(client))
