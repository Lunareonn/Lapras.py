from discord.ext import commands
from funcs import actions
import owo


class Memes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.conn, ctx.guild.id, "memes")
        if selected_cog:
            return False
        return True

    @commands.has_permissions(moderate_members=True)
    @commands.command()
    async def owofy(self, ctx):
        if ctx.message.reference is None:
            return
        else:
            if ctx.message.reference is not None:
                message = await ctx.fetch_message(ctx.message.reference.message_id)
                await ctx.message.delete()
                await ctx.send(owo.owo(message.clean_content), reference=ctx.message.reference, mention_author=False)


async def setup(client):
    await client.add_cog(Memes(client))
