import discord
import sqlite3
from discord.ext import commands
import datetime
import json

class Actionlogs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect("database.db")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def setlogs(self, ctx, channel):
        pass

    @commands.Cog.listener() # Message Edit Log
    async def on_message_edit(self, message_before, message_after):
        if message_before.author.bot:
            return

        if len(message_before.embeds) > 0 or len(message_after.embeds) > 0:
            return

        embed=discord.Embed(title="Message edited in <#{}>".format(message_before.channel.id), description="", color=0x4856ff)
        embed.set_author(name="{}#{}".format(message_before.author.name, message_before.author.discriminator), icon_url=message_before.author.display_avatar)
        embed.add_field(name="Before:", value=message_before.content, inline=False)
        embed.add_field(name="After:", value=message_after.content, inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text='')

        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)

        await channel.send(embed=embed)

    @commands.Cog.listener() # Message Delete Log
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        if len(message.attachments) != 0:
            attachment = message.attachments[0]
            embed=discord.Embed(title="Message deleted in <#{}>".format(message.channel.id), description="", color=0xfb4d70)
            embed.set_author(name="{}#{}".format(message.author.name, message.author.discriminator), icon_url=message.author.display_avatar)
            embed.add_field(name="Message Content:", value=message.content, inline=False)
            for attachment_id in range(len(message.attachments)):
                embed.add_field(name="Attachment {}".format(attachment_id+1), value="[View Attachment]({})".format(message.attachments[attachment_id].url))
            embed.add_field(name="Message Author:", value="<@{}>".format(message.author.id), inline=False)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text='')

            with open('config.json', 'r') as f:
                config = json.load(f)

            channel_id = config['logs'][0]['logs_channel_id']
            channel = self.client.get_channel(channel_id)
            await channel.send(embed=embed)
        else:
            embed=discord.Embed(title="Message deleted in <#{}>".format(message.channel.id), description="", color=0xfb4d70)
            embed.set_author(name="{}#{}".format(message.author.name, message.author.discriminator), icon_url=message.author.display_avatar)
            embed.add_field(name="Message Content:", value=message.content, inline=False)
            embed.add_field(name="Message Author:", value="<@{}>".format(message.author.id), inline=False)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text='')

            with open('config.json', 'r') as f:
                config = json.load(f)

            channel_id = config['logs'][0]['logs_channel_id']
            channel = self.client.get_channel(channel_id)
            await channel.send(embed=embed)

    @commands.Cog.listener() # Member Join Log
    async def on_member_join(self, member):
        embed=discord.Embed(title="A member has joined", description="<@{}> ({}#{}) has joined the server!".format(member.id, member.name, member.discriminator), color=0x4fff1c)
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Account Age", value="<t:{}:R>".format(int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())), inline=False)
        embed.add_field(name="Creation Date", value="<t:{}:D>".format(int(datetime.datetime.fromisoformat(str(member.created_at)).timestamp())), inline=False)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="Member Count: {} ".format(member.guild.member_count))

        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener() # Member Leave Log
    async def on_member_remove(self, member):
        try:
            await member.guild.fetch_ban(member)
            return
        except discord.NotFound:
            embed=discord.Embed(title="A member has left", description="<@{}> ({}#{}) has left the server!".format(member.id, member.name, member.discriminator), color=0xa7124a)
            embed.set_thumbnail(url=member.display_avatar)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text="Member Count: {} ".format(member.guild.member_count))

            with open('config.json', 'r') as f:
                config = json.load(f)

            channel_id = config['logs'][0]['logs_channel_id']
            channel = self.client.get_channel(channel_id)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        embed=discord.Embed(title="A member has been banned", description="<@{}> ({}#{}) has been banned!".format(member.id, member.name, member.discriminator), color=0xa7124a)
        embed.set_thumbnail(url=member.display_avatar)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="Member Count: {} ".format(member.guild.member_count))

        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        embed=discord.Embed(title="A member has been unbanned", description="<@{}> ({}#{}) has been unbanned!".format(member.id, member.name, member.discriminator), color=0xa7124a)
        embed.set_thumbnail(url=member.display_avatar)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="Member Count: {} ".format(member.guild.member_count))

        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed=discord.Embed(title="A role has been created", description="Role name: {}".format(role.name))
        embed.timestamp = datetime.datetime.now()
        
        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed=discord.Embed(title="A role has been deleted", description="Role name: {}".format(role.name))
        embed.timestamp = datetime.datetime.now()

        with open('config.json', 'r') as f:
            config = json.load(f)

        channel_id = config['logs'][0]['logs_channel_id']
        channel = self.client.get_channel(channel_id)
        await channel.send(embed=embed)


async def setup(client):
    await client.add_cog(Actionlogs(client))
