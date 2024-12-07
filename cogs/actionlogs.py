import discord
import datetime
from discord.ext import commands
from funcs import actions


class Actionlogs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.pconn = client.pconn

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.pconn, ctx.guild.id, "actionlogs")
        if selected_cog:
            return False
        return True

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def setlogs(self, ctx, channel: discord.TextChannel):
        actions.set_config_actionlog(self.client.pconn, ctx.message.guild.id, channel.id)
        await ctx.send(f"Set actionlog channel to <#{channel.id}>")

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_before.author.bot:
            return

        if len(message_before.embeds) > 0 or len(message_after.embeds) > 0:
            return

        embed = discord.Embed(title=f"Message edited in <#{message_before.channel.id}>", description="", color=0x4856ff)
        embed.set_author(name=f"{message_before.author}", icon_url=message_before.author.display_avatar)
        embed.add_field(name="Before:", value=message_before.content, inline=False)
        embed.add_field(name="After:", value=message_after.content, inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text='')

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.pconn, message_before.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        if len(message.attachments) != 0:
            embed = discord.Embed(title=f"Message deleted in <#{message.channel.id}>", description="", color=0xfb4d70)
            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar)
            embed.add_field(name="Message Content:", value=message.content, inline=False)
            for attachment_id in range(len(message.attachments)):
                embed.add_field(name=f"Attachment {attachment_id + 1}", value=f"[View Attachment]({message.attachments[attachment_id].url})")
            embed.add_field(name="Message Author:", value=f"<@{message.author.id}>", inline=False)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text='')

            channel_id = actions.fetch_actionlog_channel(self.client.pconn, message.guild.id)
            channel = await self.client.fetch_channel(channel_id)
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title=f"Message deleted in <#{message.channel.id}>", description="", color=0xfb4d70)
            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar)
            embed.add_field(name="Message Content:", value=message.content, inline=False)
            embed.add_field(name="Message Author:", value=f"<@{message.author.id}>", inline=False)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text='')

            try:
                channel_id = actions.fetch_actionlog_channel(self.client.pconn, message.guild.id)
            except TypeError:
                return
            channel = await self.client.fetch_channel(channel_id)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title="A member has joined", description=f"<@{member.id}> ({member.name}) has joined the server!", color=0x4fff1c)
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Account Age", value=f"<t:{int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())}:R>", inline=False)
        embed.add_field(name="Creation Date", value=f"<t:{int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())}:D>", inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"Member Count: {member.guild.member_count}")

        channel_id = actions.fetch_actionlog_channel(self.client.pconn, member.guild.id)
        channel = await self.client.fetch_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            await member.guild.fetch_ban(member)
            return
        except discord.NotFound:
            embed = discord.Embed(title="A member has left", description=f"<@{member.id}> ({member.name}) has left the server!", color=0xa7124a)
            embed.set_thumbnail(url=member.display_avatar)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f"Member Count: {member.guild.member_count} ")

            try:
                channel_id = actions.fetch_actionlog_channel(self.client.pconn, member.guild.id)
            except TypeError:
                return
            channel = await self.client.fetch_channel(channel_id)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="A role has been created", description=f"Role name: {role.name}")
        embed.timestamp = datetime.datetime.now()

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.pconn, role.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="A role has been deleted", description=f"Role name: {role.name}")
        embed.timestamp = datetime.datetime.now()

        try:
            channel_id = actions.fetch_actionlog_channel(self.client.pconn, role.guild.id)
        except TypeError:
            return
        channel = await self.client.fetch_channel(channel_id)
        await channel.send(embed=embed)


async def setup(client):
    await client.add_cog(Actionlogs(client))
