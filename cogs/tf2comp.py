from funcs import actions
from discord.ext import commands


class TF2Comp(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.pconn, ctx.guild.id, "tf2comp")
        if selected_cog:
            return False
        return True


async def setup(client):
    await client.add_cog(TF2Comp(client))
