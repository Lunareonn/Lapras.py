import discord
import sqlite3
import platform
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('databases/database.db')

    @commands.hybrid_group()
    @commands.is_owner()
    async def presence(self, ctx):
        await ctx.send("Incorrect syntax! Try `presence set` or `presence clear`")

    @commands.is_owner()
    @presence.command()
    async def set(self, ctx, presence: str):
        await self.client.change_presence(activity=discord.Game(presence))
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("**WARNING!** ``discord.Forbidden`` was raised! I may be missing important permissions.")
        await ctx.send(f"Done! Changed presence to `{presence}`")

    @commands.is_owner()
    @presence.command()
    async def clear(self, ctx):
        await self.client.change_presence(activity=None)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("**WARNING!** ``discord.Forbidden`` was raised! I may be missing important permissions.")
        await ctx.send("Done! Presence cleared.")

    @commands.command()
    async def ping(self, ctx):
        latency = self.client.latency
        await ctx.send(f"Ping! In {round(latency * 1000)}ms")

    @commands.command()
    async def setautorole(self, ctx, role: discord.Role):
        roleid = role.id
        id = ctx.guild.id
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO \"{id}\" (cname, cvalue) VALUES(?, ?);", ("autorole", roleid))
        self.conn.commit()
        await ctx.send(f"Autorole set! New members will be assigned <@&{roleid}>")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        id = member.guild.id
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT cname, cvalue FROM \"{id}\" WHERE cname = 'autorole'")
        roleid = cursor.fetchone()[1]
        role = member.guild.get_role(roleid)
        await member.add_roles(role)

    @commands.command()
    async def who(self, ctx, member: discord.Member):
        userid = member.id
        username = member.name
        displayname = member.global_name
        user_avatar = member.avatar
        user_perms = member.guild_permissions
        created_at = member.created_at.strftime("%d/%m/%Y, %H:%M:%S")
        joined_at = member.joined_at.strftime("%d/%m/%Y, %H:%M:%S")

        staff = False
        owner = False

        if user_avatar is None:
            user_avatar = member.default_avatar

        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                custom_status = activity.name
                break
            else:
                custom_status = None

        if user_perms.ban_members or user_perms.kick_members or user_perms.manage_members:
            staff = True
        if ctx.guild.owner_id == userid:
            owner = True

        embed = discord.Embed(description=f"<@{userid}> ({username})", color=0x2f96fd)
        embed.set_thumbnail(url=user_avatar.url)
        embed.add_field(name="Joined Server", value=joined_at, inline=True)
        embed.add_field(name="Creation Date", value=created_at, inline=True)
        embed.add_field(name="Username", value=username, inline=False)
        embed.add_field(name="Display name", value=displayname, inline=False)
        embed.add_field(name="Staff?", value=staff, inline=False)
        embed.add_field(name="Owner?", value=owner, inline=False)
        embed.add_field(name="Custom status", value=custom_status, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        client = ctx.bot.user
        author = await self.client.fetch_user(237605319159709696)

        embed = discord.Embed(title="Lapras.py", url="https://github.com/Lunareonn", description="Lapras is a multi-function bot created by Lunareonn", color=0x399bfd)
        embed.set_thumbnail(url=client.avatar.url)
        embed.add_field(name="Author", value=f"<@{author.id}>", inline=True)
        embed.add_field(name="Version", value="1.0.0-dev", inline=True)
        embed.set_footer(text=f"Discord.py {discord.__version__} | Python {platform.python_version()}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def dbtest(self, ctx):
        id = ctx.message.guild.id
        conn_config = sqlite3.connect("databases/database.db")
        conn_macros = sqlite3.connect("databases/macros.db")

        config_cursor = conn_config.cursor()
        macros_cursor = conn_macros.cursor()

        embed = discord.Embed(title="Checking database...",
                              description="Checking database.db",
                              colour=0xffffff)

        embed.add_field(name="database.db",
                        value="?",
                        inline=True)
        embed.add_field(name="macros.db",
                        value="?",
                        inline=True)

        dbmessage = await ctx.send(embed=embed)
        configcheck = config_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{id}';").fetchall()
        if configcheck == []:
            config = False
            embed.set_field_at(index=0, name="database.db", value="FAIL", inline=True)
            await dbmessage.edit(embed=embed)
        else:
            config = True
            embed.set_field_at(index=0, name="database.db", value="PASS", inline=True)
            await dbmessage.edit(embed=embed)

        macroscheck = macros_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{id}';").fetchall()
        if macroscheck == []:
            macro = False
            embed.set_field_at(index=1, name="database.db", value="FAIL", inline=True)
            await dbmessage.edit(embed=embed)
        else:
            macro = True
            embed.set_field_at(index=1, name="macros.db", value="PASS", inline=True)

        if config is False or macro is False:
            embed = discord.Embed(title="Fixing databases...",
                                  description="Fixing database.db",
                                  colour=0xf40006)
            if config is True:
                embed.add_field(name="database.db", value="PASS", inline=True)
            else:
                embed.add_field(name="database.db", value="?", inline=True)

            if macro is True:
                embed.add_field(name="macros.db", value="PASS", inline=True)
            else:
                embed.add_field(name="macros.db", value="?", inline=True)

            await dbmessage.edit(embed=embed)
            if config is False:
                conn_config.execute(f"CREATE TABLE IF NOT EXISTS \"{id}\" (cname TEXT, cvalue NULL);")
                conn_config.commit()
                configcheck = config_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{id}';").fetchall()
                if configcheck != []:
                    embed.set_field_at(index=0, name="database.db", value="PASS", inline=True)

                await dbmessage.edit(embed=embed)
            else:
                embed.set_field_at(index=0, name="database.db", value="PASS", inline=True)
                await dbmessage.edit(embed=embed)

            if macro is False:
                conn_macros.execute(f"CREATE TABLE IF NOT EXISTS \"{id}\" (name TEXT, alias TEXT, content TEXT);")
                conn_macros.commit()
                macroscheck = config_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{id}';").fetchall()
                if macroscheck != []:
                    embed.set_field_at(index=1, name="macros.db", value="PASS", inline=True)

                await dbmessage.edit(embed=embed)
            else:
                embed.set_field_at(index=1, name="macros.db", value="PASS", inline=True)
                await dbmessage.edit(embed=embed)

            embed = discord.Embed(title="Done!",
                                  description="Databases fixed.",
                                  colour=0x0ff103)
            embed.add_field(name="database.db", value="PASS", inline=True)
            embed.add_field(name="macros.db", value="PASS", inline=True)
            await dbmessage.edit(embed=embed)

        if config is True and macro is True:
            embed = discord.Embed(title="Done!",
                                  description="Nothing needs to be done.",
                                  colour=0x0ff103)
            embed.add_field(name="database.db", value="PASS", inline=True)
            embed.add_field(name="macros.db", value="PASS", inline=True)
            await dbmessage.edit(embed=embed)
        else:
            pass


async def setup(client):
    await client.add_cog(Utility(client))
