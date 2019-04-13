from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils import checks, pyson

config = pyson.Pyson("data/config/startup.json")


class Owner(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.command(aliases=["sp", "prefix"])
    @checks.is_guild_owner()
    async def set_prefix(self, ctx, prefix: str = None):
        """: Change the prefix of the bot, up to two chars."""
        if not prefix:
            prefix = (
                self.bot.config.data.get("servers").get(str(ctx.guild.id)).get("prefix")
            )
            await ctx.send(f"current prefix is {prefix}")
            return
        else:
            if len(prefix) >= 3:
                await ctx.send("Prefix length too long.")
                return

            self.bot.config.data["servers"][str(ctx.guild.id)]["prefix"] = prefix
            self.bot.config.save()
            await ctx.send(f"Prefix updated to {prefix}")


def setup(bot):
    bot.add_cog(Owner(bot))
    log.info("Cog loaded: Owner")
