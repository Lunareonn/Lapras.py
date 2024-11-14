import discord
import datetime
import config
from enum import Enum
from funcs import actions
from funcs.checks import check_if_leader
from discord.ext import commands


class ClassEnum(Enum):
    Scout = 0
    Soldier = 1
    Pyro = 2
    Demo = 3
    Heavy = 4
    Engineer = 5
    Medic = 6
    Sniper = 7
    Spy = 8


class TF2Comp(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn
        self.available_players = []
        self.unavailable_players = []
        self.vote_message_id = None

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.conn, ctx.guild.id, "tf2comp")
        if selected_cog:
            return False
        return True

    @commands.check(check_if_leader)
    @commands.command()
    async def available(self, ctx):
        await ctx.message.delete()

        self.available_players.clear()
        self.unavailable_players.clear()

        embed = discord.Embed(title="Roster availability",
                              description=u"React with \u2705 or \u274E",
                              colour=0x0aebeb,
                              timestamp=datetime.datetime.now())
        embed.add_field(name="Scout",
                        value="?",
                        inline=True)
        embed.add_field(name="Soldier",
                        value="?",
                        inline=True)
        embed.add_field(name="Pyro",
                        value="?",
                        inline=True)
        embed.add_field(name="Demo",
                        value="?",
                        inline=True)
        embed.add_field(name="Heavy",
                        value="?",
                        inline=True)
        embed.add_field(name="Engineer",
                        value="?",
                        inline=True)
        embed.add_field(name="Medic",
                        value="?",
                        inline=True)
        embed.add_field(name="Sniper",
                        value="?",
                        inline=True)
        embed.add_field(name="Spy",
                        value="?",
                        inline=True)

        embed.set_footer(text=":3")
        message = await ctx.send(embed=embed)
        actions.add_availability_message(self.client.conn, ctx.guild.id, message.id)
        self.vote_message_id = message.id
        await message.add_reaction(u"\u2705")
        await message.add_reaction(u"\u274E")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        main_roles = config.main_or_sub
        roster_roles = config.roster_roles

        channel = self.client.get_channel(payload.channel_id)
        message_id = actions.fetch_availability_message(self.client.conn, payload.guild_id)
        vote_message = await channel.fetch_message(message_id)
        member = await channel.guild.fetch_member(payload.user_id)

        embed = discord.Embed(title="Roster availability",
                              description=u"React with \u2705 or \u274E",
                              colour=0x0aebeb,
                              timestamp=datetime.datetime.now())
        embed.add_field(name="Scout",
                        value="?",
                        inline=True)
        embed.add_field(name="Soldier",
                        value="?",
                        inline=True)
        embed.add_field(name="Pyro",
                        value="?",
                        inline=True)
        embed.add_field(name="Demo",
                        value="?",
                        inline=True)
        embed.add_field(name="Heavy",
                        value="?",
                        inline=True)
        embed.add_field(name="Engineer",
                        value="?",
                        inline=True)
        embed.add_field(name="Medic",
                        value="?",
                        inline=True)
        embed.add_field(name="Sniper",
                        value="?",
                        inline=True)
        embed.add_field(name="Spy",
                        value="?",
                        inline=True)

        if payload.member == self.client.user:
            return

        try:
            if payload.message_id == message_id:
                is_main = any(role.id in main_roles for role in member.roles)
                class_role = any(role.id in roster_roles for role in member.roles)
                if payload.emoji.name == u'\u2705':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                actions.append_available_players(self.client.conn, payload.guild_id, message_id, payload.user_id, role.id)
                                class_id = config.roster_roles.index(role.id)
                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="Yes", inline=True)
                                self.available_players.append(payload.user_id)
                                print("+ AV:", self.available_players)
                                await vote_message.edit(embed=embed)
                                break
                    else:
                        await vote_message.remove_reaction(u'\u2705', member)

                if payload.emoji.name == u'\u274E':
                    if is_main and class_role:
                        for role in payload.member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)
                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="No", inline=True)
                                self.unavailable_players.append(payload.user_id)
                                print("+ UNAV:", self.unavailable_players)
                                await vote_message.edit(embed=embed)
                                break
                    else:
                        await vote_message.remove_reaction(u'\u274E', member)
        except Exception as e:
            self.client.log.exception(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        main_roles = config.main_or_sub
        roster_roles = config.roster_roles

        channel = self.client.get_channel(payload.channel_id)
        vote_message = await channel.fetch_message(self.vote_message_id)
        member = await channel.guild.fetch_member(payload.user_id)

        embed = discord.Embed(title="Roster availability",
                              description=u"React with \u2705 or \u274E",
                              colour=0x0aebeb,
                              timestamp=datetime.datetime.now())

        if payload.member == self.client.user:
            return

        try:
            if payload.message_id == self.vote_message_id:
                is_main = any(role.id in main_roles for role in member.roles)
                class_role = any(role.id in roster_roles for role in member.roles)
                if payload.emoji.name == u'\u2705':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="?", inline=True)
                                self.available_players.remove(payload.user_id)
                                print("- AV:", self.available_players)
                                await vote_message.edit(embed=embed)
                                break

                if payload.emoji.name == u'\u274E':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="?", inline=True)
                                self.unavailable_players.remove(payload.user_id)
                                print("- UNAV:", self.unavailable_players)
                                await vote_message.edit(embed=embed)
                                break
        except Exception as e:
            self.client.log.exception(e)


async def setup(client):
    await client.add_cog(TF2Comp(client))
