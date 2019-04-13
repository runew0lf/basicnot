from discord import Embed
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from loguru import logger as log
import itertools
from .utils.pagination import LinePaginator


class MyHelpCommand(commands.DefaultHelpCommand):
    def get_command_signature(self, command):
        return "{0.clean_prefix}{1.qualified_name} {1.signature}".format(self, command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        lines = []

        no_category = "\u200b{0.no_category}:".format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ":" if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            commands = (
                sorted(commands, key=lambda c: c.name)
                if self.sort_commands
                else list(commands)
            )
            lines.append(f"**__{category}__**")
            for command in commands:
                lines.append(f"**{ctx.prefix}{command.name}** - {command.short_doc}")

        note = self.get_ending_note()
        if not note:
            note = ""

        embed = Embed(color=ctx.me.color, title=f"{ctx.guild.name}")

        embed.set_author(
            name=f"{bot.user.name} Help Manual",
            icon_url=bot.user.avatar_url_as(format="png"),
        )
        destination = self.get_destination()
        await LinePaginator.paginate(
            (line for line in lines),
            destination,
            embed,
            bot,
            footer_text=note,
            max_lines=10,
            empty=False,
        )

    async def send_cog_help(self, cog):
        ctx = self.context
        bot = ctx.bot
        destination = self.get_destination()
        lines = []

        filtered = await self.filter_commands(
            cog.get_commands(), sort=self.sort_commands
        )
        lines.append(f"**__{cog.description}__**")
        for command in filtered:
            lines.append(f"**{ctx.prefix}{command.name}** - {command.short_doc}")

        note = self.get_ending_note()
        if not note:
            note = ""

        lines.append(f"**{ctx.prefix}{command.name}** - {command.description}")

        embed = Embed(color=ctx.me.color, title=f"{ctx.guild.name}")

        embed.set_author(
            name=f"{bot.user.name} Help Manual",
            icon_url=bot.user.avatar_url_as(format="png"),
        )
        await LinePaginator.paginate(
            (line for line in lines),
            destination,
            embed,
            bot,
            footer_text=note,
            max_lines=10,
            empty=False,
        )

    async def send_command_help(self, command):
        ctx = self.context
        bot = ctx.bot
        destination = self.get_destination()

        note = self.get_ending_note()
        if not note:
            note = ""
        embed = Embed(color=ctx.me.color, title=f"{ctx.guild.name}")
        embed.set_author(
            name=f"{bot.user.name} Help Manual",
            icon_url=bot.user.avatar_url_as(format="png"),
        )
        embed.set_footer(text=note)
        embed.description = f"**__{ctx.prefix}{command.name}__**\n{command.help}"
        await destination.send(embed=embed)


class MyCog(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(MyCog(bot))
    log.info("Cog loaded: MyCog")
