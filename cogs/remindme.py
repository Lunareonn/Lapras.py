from funcs import actions
from discord.ext import commands


class Remindme(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn

    @commands.command()
    async def remindme(self, ctx, time, *, message: str):
        remind_at = actions.get_timedelta(time)
        actions.add_reminder(self.client.conn, ctx.guild.id, ctx.author.id, remind_at, message)


async def setup(client):
    await client.add_cog(Remindme(client))
