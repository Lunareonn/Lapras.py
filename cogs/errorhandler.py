import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, discord.ClientException):
                await ctx.send("``discord.ClientException`` raised! You must've done something wrong for this to pop up.")
            elif isinstance(original, discord.RateLimited):
                await ctx.send("``discord.RateLimited`` raised! The bot is being ratelimited by discord. Please wait before doing anything.")
            elif isinstance(original, discord.Forbidden):
                await ctx.send(f"``discord.Forbidden`` raised! I'm not allowed to do what you asked of me.\nDetails: ``{original}``")
            elif isinstance(original, discord.NotFound):
                await ctx.send("``discord.NotFound`` raised! Whatever you were looking for was not found.")
                print(original)
            elif isinstance(original, discord.DiscordServerError):
                await ctx.send("``discord.DiscordServerError`` raised! This is entirely discord's fault. Ping Luna if issue persists.")
            elif isinstance(original, discord.InvalidData):
                await ctx.send("``discord.InvalidData`` raised! Discord sent me invalid data. Ping Luna if issue persists.")
            elif isinstance(original, discord.HTTPException):
                await ctx.send(f"``discord.HTTPException`` raised! an HTTP request failed. Ping Luna if issue persists.\nDetails: ``{original}``")
            elif isinstance(original, discord.DiscordException):
                await ctx.send("``discord.DiscordException`` raised! Something failed over on the bot's side. Ping Luna if issue persists.")
            else:
                raise error


async def setup(client):
    await client.add_cog(ErrorHandler(client))
