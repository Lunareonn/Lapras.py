# import discord
import sqlite3
from discord.ext import commands


class Macros(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('databases/macros.db')

    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def macroadd(self, ctx, name: str, *, content: str):
        id = ctx.message.guild.id

        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM \"{id}\"")
        rows = cursor.fetchall()
        for r in rows:
            if r == name:
                return await ctx.send("That macro already exists.")

        try:
            cursor.execute(f"INSERT INTO \"{id}\" (name, content) VALUES(?, ?);", (name, content,))
        except sqlite3.OperationalError:
            return await ctx.send("``sqlite3.OperationalError`` raised! Something's wrong with ``config.db``. Please ping Luna.")

        self.conn.commit()
        await ctx.send(f"Added macro {name}")

    @macroadd.error
    async def marcoadd_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")

    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def macroremove(self, ctx, name):
        id: str = ctx.message.guild.id
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"DELETE FROM \"{id}\" WHERE name = ?", (name,))
        except sqlite3.OperationalError:
            return await ctx.send("``sqlite3.OperationalError`` raised! Something's wrong with ``macros.db``. Please ping Luna.")

        self.conn.commit()
        await ctx.send(f"Removed macro {name}")

    @macroremove.error
    async def marcoremove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<@{ctx.author.id}>: Not enough arguments! {error}")

    @commands.hybrid_command()
    async def m(self, ctx, name):
        id = ctx.message.guild.id
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name, content FROM \"{id}\"")
        macro = cursor.fetchall()

        for m in macro:
            content = None
            if m[0] == name:
                content = str(m[1])
                pass

        if content is None:
            return await ctx.send(f"<@{ctx.message.author.id}>: Macro '{name}' is not a valid macro")

        await ctx.send(f"{content}")

    @m.error
    async def m_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't specify a macro.")
        else:
            raise error

    @commands.hybrid_command()
    async def macros(self, ctx):
        id = ctx.message.guild.id
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM \"{id}\"")
        macro = cursor.fetchall()

        macros = "**Available macros:**\n"

        for m in macro:
            macros += "- " + m[0] + "\n"

        await ctx.send(macros)


async def setup(client):
    await client.add_cog(Macros(client))
