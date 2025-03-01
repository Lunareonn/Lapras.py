# import discord
# import datetime
# import config
from enum import Enum
from funcs import actions
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
        self.available_players = []
        self.unavailable_players = []
        self.vote_message_id = None

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.pconn, ctx.guild.id, "tf2comp")
        if selected_cog:
            return False
        return True


async def setup(client):
    await client.add_cog(TF2Comp(client))
