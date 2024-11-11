import mariadb
from funcs import actions
from discord.ext import commands


class Macros(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.conn, ctx.guild.id, "macros")
        if selected_cog:
            return False
        return True

    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def macroadd(self, ctx, name: str, *, content: str):
        try:
            actions.add_macro(self.client.conn, ctx.message.guild.id, name, content)
        except mariadb.IntegrityError:
            await ctx.send(f"Macro ``{name}`` already exists")
            return
        await ctx.send(f"Added macro ``{name}``")

    @macroadd.error
    async def marcoadd_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")

    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def macroremove(self, ctx, name):
        actions.delete_macro(self.client.conn, name)
        await ctx.send(f"Removed macro {name}")

    @macroremove.error
    async def marcoremove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")

    @commands.hybrid_command()
    async def m(self, ctx, name):
        try:
            content = actions.fetch_macro(self.client.conn, ctx.message.guild.id, name)
        except TypeError:
            await ctx.send(f"``{name}`` is not a valid macro.")

        await ctx.message.delete()
        await ctx.send(f"{content}")

    @m.error
    async def m_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't specify a macro.")
        else:
            raise error

    @commands.hybrid_command()
    async def macros(self, ctx):
        macros = actions.fetch_macro_list(self.client.conn, ctx.message.guild.id)

        macros_string = "**Available macros:**\n"
        macros_list = ""

        for m in macros:
            macros_list += f"- {m[0]}\n"

        await ctx.send(macros_string + macros_list)


async def setup(client):
    await client.add_cog(Macros(client))
