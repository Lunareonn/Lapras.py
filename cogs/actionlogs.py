import discord
import sqlite3
from discord.ext import commands
import datetime


class Actionlogs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect("databases/config.db")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def setlogs(self, ctx, channel: discord.TextChannel):
        id = ctx.message.guild.id

        channelid = str(channel.id)
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"DELETE FROM \"{id}\" WHERE cname = ?;", ("actionlogs_channel", ))
            cursor.execute(f"INSERT INTO \"{id}\" (cname, cvalue) VALUES(?, ?);", ("actionlogs_channel", channelid))
        except sqlite3.OperationalError:
            return await ctx.send("``sqlite3.OperationalError`` raised! Something's wrong with ``config.db``. Please ping Luna.")

        self.conn.commit()
        await ctx.send(f"Set actionlog channel to <#{channelid}>")

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        id = str(message_before.guild.id)

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

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
        except sqlite3.OperationalError:
            return
        channelid = cursor.fetchone()[1]
        channel = await self.client.fetch_channel(channelid)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        id = str(message.guild.id)

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

            cursor = self.conn.cursor()
            try:
                cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
            except sqlite3.OperationalError:
                return
            channelid = cursor.fetchone()[1]
            channel = await self.client.fetch_channel(channelid)

            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title=f"Message deleted in <#{message.channel.id}>", description="", color=0xfb4d70)
            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar)
            embed.add_field(name="Message Content:", value=message.content, inline=False)
            embed.add_field(name="Message Author:", value=f"<@{message.author.id}>", inline=False)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text='')

            cursor = self.conn.cursor()
            try:
                cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
            except sqlite3.OperationalError:
                return
            channelid = cursor.fetchone()[1]
            channel = await self.client.fetch_channel(channelid)

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        id = member.guild.id

        embed = discord.Embed(title="A member has joined", description=f"<@{member.id}> ({member.name}) has joined the server!", color=0x4fff1c)
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Account Age", value=f"<t:{int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())}:R>", inline=False)
        embed.add_field(name="Creation Date", value=f"<t:{int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())}:D>", inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"Member Count: {member.guild.member_count}")

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
        except sqlite3.OperationalError:
            return
        channelid = cursor.fetchone()[1]
        channel = await self.client.fetch_channel(channelid)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        id = member.guild.id

        try:
            await member.guild.fetch_ban(member)
            return
        except discord.NotFound:
            embed = discord.Embed(title="A member has left", description=f"<@{member.id}> ({member.name}) has left the server!", color=0xa7124a)
            embed.set_thumbnail(url=member.display_avatar)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f"Member Count: {member.guild.member_count} ")

            cursor = self.conn.cursor()
            try:
                cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
            except sqlite3.OperationalError:
                return
            channelid = cursor.fetchone()[1]
            channel = await self.client.fetch_channel(channelid)

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        id = role.guild.id

        embed = discord.Embed(title="A role has been created", description=f"Role name: {role.name}")
        embed.timestamp = datetime.datetime.now()

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
        except sqlite3.OperationalError:
            return
        channelid = cursor.fetchone()[1]
        channel = await self.client.fetch_channel(channelid)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        id = role.guild.id

        embed = discord.Embed(title="A role has been deleted", description=f"Role name: {role.name}")
        embed.timestamp = datetime.datetime.now()

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'actionlogs_channel'")
        except sqlite3.OperationalError:
            return
        channelid = cursor.fetchone()[1]
        channel = await self.client.fetch_channel(channelid)

        await channel.send(embed=embed)


async def setup(client):
    await client.add_cog(Actionlogs(client))
