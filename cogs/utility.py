import discord
import re
import platform
import config
from funcs import actions
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.conn = client.conn

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
        actions.set_config_autorole(self.client.conn, ctx.guild.id, role.id)
        await ctx.send(f"Autorole set! New members will be assigned <@&{role.id}>")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            role_id = actions.fetch_autorole(self.client.conn, member.guild.id)
        except TypeError:
            return
        role = member.guild.get_role(role_id)
        await member.add_roles(role)

    @commands.command()
    async def who(self, ctx, member: discord.Member):
        user_id = member.id
        username = member.name
        display_name = member.global_name
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
        if ctx.guild.owner_id == user_id:
            owner = True

        embed = discord.Embed(description=f"<@{user_id}> ({username})", color=0x2f96fd)
        embed.set_thumbnail(url=user_avatar.url)
        embed.add_field(name="Joined Server", value=joined_at, inline=True)
        embed.add_field(name="Creation Date", value=created_at, inline=True)
        embed.add_field(name="Username", value=username, inline=False)
        embed.add_field(name="Display name", value=display_name, inline=False)
        embed.add_field(name="Staff?", value=staff, inline=False)
        embed.add_field(name="Owner?", value=owner, inline=False)
        embed.add_field(name="Custom status", value=custom_status, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        author = await self.client.fetch_user(237605319159709696)

        embed = discord.Embed(title="Lapras.py", url="https://github.com/Lunareonn/Lapras.py", description="Lapras is a multifunctional bot created by Lunareonn", color=0x399bfd)
        embed.add_field(name="Author", value=f"<@{author.id}>", inline=True)
        embed.add_field(name="Version", value=config.bot_version, inline=True)
        embed.set_footer(text=f"Discord.py {discord.__version__} | Python {platform.python_version()}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def manualregister(self, ctx):
        cur = self.client.conn.cursor()
        cur.execute("SELECT server_id FROM servers WHERE server_id = ?", (ctx.guild.id,))
        if cur.fetchone() is not None:
            return await ctx.send(f"Server {ctx.guild.id} already in database")
        else:
            actions.register_server(self.client.conn, ctx.guild.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        link_regex = r"https?://(?:(?:ptb|canary)\.)?discord(app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"
        link_match = re.match(link_regex, message.content)
        if link_match:
            message_id = link_match.groups()
            fetched_message = await message.channel.fetch_message(message_id[3])
        else:
            return

        embed = discord.Embed(description=f"{fetched_message.content}", colour=0x05c7ef)
        embed.set_author(name=f"{fetched_message.author}", icon_url=f"{fetched_message.author.display_avatar.url}")
        embed.add_field(name="Jump to message",
                        value=f"[Click here]({fetched_message.jump_url})",
                        inline=False)

        await message.delete()
        await message.channel.send(embed=embed)

    @commands.hybrid_group()
    async def cog(self, ctx):
        await ctx.send("Incorrect syntax! Try `cog enable <cog>` or `cog disable <cog>`")

    @cog.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, cog: str):
        valid_cog = actions.enable_cog(self.client.conn, ctx.guild.id, cog)
        if valid_cog is False:
            await ctx.send(f"{cog} is not a valid cog.")
            return
        await ctx.send(f"Successfully enabled {cog}!")

    @cog.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, cog: str):
        valid_cog = actions.disable_cog(self.client.conn, ctx.guild.id, cog)
        if valid_cog is False:
            await ctx.send(f"{cog} is not a valid cog.")
            return
        await ctx.send(f"Successfully disabled {cog}!")

    @cog.command()
    async def list(self, ctx):
        disabled_cogs = actions.list_disabled_cogs(self.client.conn, ctx.guild.id)

        cogs_string = f"**Disabled cogs on {ctx.guild.name}:**\n"
        cogs_list = ""

        for c in disabled_cogs:
            if None in c:
                continue
            cogs_list += f"- {c[0]}\n"

        await ctx.send(cogs_string + cogs_list)


async def setup(client):
    await client.add_cog(Utility(client))
