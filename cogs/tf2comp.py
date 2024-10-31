import os
import sys
import discord
import re
import grpc
import datetime
import requests
import json
import logging
import config
from enum import Enum
from funcs.checks import check_if_leader
from io import BytesIO
from PIL import Image
from time import strftime, localtime
from discord.ext import commands
from funcs import htmlgen

sys.path.append("gRPC")
import screenshot_pb2, screenshot_pb2_grpc


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

        global available_players
        global unavailable_players
        available_players = []
        unavailable_players = []

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        regex_logs = r"http(s|):\/\/(www\.|)logs\.tf\/\d+"
        text_logs = re.search(regex_logs, message.content)

        # Temporarily disables this feature
        return

        if text_logs:
            try:
                channel = grpc.insecure_channel("localhost:50051")
                stub = screenshot_pb2_grpc.ScreenshotterStub(channel)

                log_url = text_logs.group()
                endpoint = 'https://logs.tf/api/v1/log/{}'.format(log_url[16:])

                response = requests.get(endpoint)
                response.raise_for_status()
                json_data = json.loads(response.text)
                info = json_data["info"]

                name = info['title']
                map = info['map']
                length = str(datetime.timedelta(seconds=info['total_length']))[2:]
                date = strftime('%d %b, %Y @ %I.%M %p', localtime(info['date']))

                teams = json_data['teams']
                red_team = teams['Red']
                red_score = red_team['score']
                blu_team = teams['Blue']
                blu_score = blu_team['score']

                htmlgen.generate_html(name, map, length, date, teams, red_team, red_score, blu_team, blu_score)

                screenshot_request = screenshot_pb2.TakeScreenshotRequest(url=text_logs.group(), element="#log-section-players")
                screenshot_request = screenshot_pb2.TakeScreenshotRequest(url="file:///C:/Users/LunaXCBN/Documents/Projects/Lapras.py/logs.html")
                reply = stub.TakeScreenshot(screenshot_request)

                img = Image.open(BytesIO(reply.image))

                img.save("logs.png")

                file = discord.File(fp="logs.png", filename="logs.png")
                embed = discord.Embed(title=f"{name}",
                                      url=log_url,
                                      description=f"Map: {map}\nLength: {length}\n\nBlu: **{blu_score}** | Red: **{red_score}**",
                                      colour=0xca9191)

                embed.set_author(name="logs.tf",
                                 url="https://logs.tf/",
                                 icon_url="https://logs.tf/assets/img/icon.png")

                embed.set_image(url="attachment://logs.png")

                embed.set_footer(text=f"{date}")
                await message.channel.send(embed=embed, file=file)
                os.remove("logs.png")
            except Exception as e:
                return self.client.log.exception(e)
        else:
            pass

    @commands.check(check_if_leader)
    @commands.command()
    async def available(self, ctx):
        await ctx.message.delete()
        global vote_message_id
        global embed

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
        vote_message_id = message.id
        await message.add_reaction(u"\u2705")
        await message.add_reaction(u"\u274E")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        global vote_message_id
        global embed
        main_roles = config.main_or_sub
        roster_roles = config.roster_roles

        channel = self.client.get_channel(payload.channel_id)
        vote_message = await channel.fetch_message(vote_message_id)
        member = await channel.guild.fetch_member(payload.user_id)

        if payload.member == self.client.user:
            return

        try:
            if payload.message_id == vote_message_id:
                is_main = any(role.id in main_roles for role in member.roles)
                class_role = any(role.id in roster_roles for role in member.roles)
                if payload.emoji.name == u'\u2705':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                # if payload.user_id in unavailable_players:
                                #     await vote_message.remove_reaction(u'\u274E', member)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="Yes", inline=True)
                                available_players.append(payload.user_id)
                                print("+ AV:", available_players)
                                await vote_message.edit(embed=embed)
                                break
                    else:
                        await vote_message.remove_reaction(u'\u2705', member)

                if payload.emoji.name == u'\u274E':
                    if is_main and class_role:
                        for role in payload.member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                # if payload.user_id in available_players:
                                #     await vote_message.remove_reaction(u'\u2705', member)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="No", inline=True)
                                unavailable_players.append(payload.user_id)
                                print("+ UNAV:", unavailable_players)
                                await vote_message.edit(embed=embed)
                                break
                    else:
                        await vote_message.remove_reaction(u'\u274E', member)
        except Exception as e:
            self.client.log.exception(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        global vote_message_id
        global embed
        main_roles = config.main_or_sub
        roster_roles = config.roster_roles

        channel = self.client.get_channel(payload.channel_id)
        vote_message = await channel.fetch_message(vote_message_id)
        member = await channel.guild.fetch_member(payload.user_id)

        if payload.member == self.client.user:
            return

        try:
            if payload.message_id == vote_message_id:
                is_main = any(role.id in main_roles for role in member.roles)
                class_role = any(role.id in roster_roles for role in member.roles)
                if payload.emoji.name == u'\u2705':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="?", inline=True)
                                available_players.remove(payload.user_id)
                                print("- AV:", available_players)
                                await vote_message.edit(embed=embed)
                                break

                if payload.emoji.name == u'\u274E':
                    if is_main and class_role:
                        for role in member.roles:
                            if role.id in config.roster_roles:
                                class_id = config.roster_roles.index(role.id)

                                embed.set_field_at(index=class_id, name=str(ClassEnum(class_id).name), value="?", inline=True)
                                unavailable_players.remove(payload.user_id)
                                print("- UNAV:", unavailable_players)
                                await vote_message.edit(embed=embed)
                                break
        except Exception as e:
            self.client.log.exception(e)


async def setup(client):
    await client.add_cog(TF2Comp(client))
