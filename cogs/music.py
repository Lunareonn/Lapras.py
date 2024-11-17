import re
import discord
from funcs import actions
from datetime import datetime
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cog_check(self, ctx):
        selected_cog = actions.check_if_cog_disabled(self.client.conn, ctx.guild.id, "music")
        if selected_cog:
            return False
        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        regex = r"https:\/\/open\.spotify\.com\/(track|album|artist|playlist)\/[a-zA-Z0-9]+"
        link_match = re.match(regex, message.content)

        if link_match:
            pass
        else:
            return

        try:
            title, artist = actions.metadata_parser(link_match[0])
            (track_url,
             album_url,
             playcount,
             duration,
             album_name,
             cover,
             genre_list) = actions.fetch_lastfm(title, artist)
        except TypeError:
            return

        minutes, seconds = actions.convertMillis(int(duration))

        embed = discord.Embed(title=f"{artist} - {title}",
                              url=f"{track_url}",
                              description=f"Album: [{album_name}]({album_url})\nDuration: {minutes}:{seconds}\nPlay count: {playcount}\n\nGenre(s): {genre_list}",
                              colour=0x00b0f4,
                              timestamp=datetime.now())
        embed.set_author(name=f"{message.author}", icon_url=f"{message.author.avatar.url}")
        embed.set_thumbnail(url=f"{cover}")
        embed.set_footer(text=":3")
        await message.channel.send(embed=embed, reference=message)


async def setup(client):
    await client.add_cog(Music(client))
