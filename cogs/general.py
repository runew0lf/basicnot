import os
import platform

import discord
import pendulum
import psutil
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils import checks


class General(commands.Cog):
    """General"""

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.voice_connection = None
        self.uptime = pendulum.now()

    @commands.command(name="clear")
    @checks.is_admin()
    async def clear(self, ctx, lines: int = 1):
        """
        Clears a number of lines from chat
        Permissions: Needs admin permissions
        """
        dellist = await ctx.channel.history(limit=int(lines) + 1).flatten()
        await ctx.channel.delete_messages(dellist)

    @commands.command(name="server")
    async def server(self, ctx):
        """
        Displays server info
        Usage: !server
        """
        server = ctx.guild
        embed = discord.Embed(title=server.name, description="", color=ctx.me.color)
        embed.set_thumbnail(url=server.icon_url)

        serverinfo = (
            f"Owner: {server.owner}\n"
            f"Created: {pendulum.instance(server.created_at).diff_for_humans()}\n"
            f"Members: {server.member_count}\n"
            f"Region: {server.region}\n"
            f"Features: {', '.join(server.features)}"
        )
        embed.add_field(name="Server Information", value=serverinfo)

        member_list = list(server.members)
        status_list = [member.status.value for member in member_list]

        membersinfo = (
            f"Online: {status_list.count('online')}\n"
            f"Idle: {status_list.count('idle')}\n"
            f"Dnd: {status_list.count('dnd')}\n"
            f"Offline: {status_list.count('offline')}"
        )

        embed.add_field(name="Channels", value=f"{len(server.channels)}", inline=True)
        embed.add_field(name="Roles", value=f"{len(server.roles)}", inline=True)
        embed.add_field(name="Members", value=membersinfo, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="info")
    async def info(self, ctx):
        """
        Displays bot information
        """
        process = psutil.Process(os.getpid())
        embed = discord.Embed(
            color=ctx.me.color,
            title=f"{ctx.me.name}",
            description=f"{ctx.me.name} has been up for {self.uptime.diff_for_humans(absolute=True)}",
        )
        embed.set_thumbnail(url=ctx.me.avatar_url)
        embed.add_field(name="» Ping", value=f"{round(self.bot.latency*1000)}ms")
        embed.add_field(name="» Servers", value=format(len(self.bot.guilds), ","))
        embed.add_field(
            name="» Users", value=format(len(list(self.bot.get_all_members())), ",")
        )
        embed.add_field(
            name="» Channels", value=format(len(list(self.bot.get_all_channels())), ",")
        )
        embed.add_field(name="» Commands", value=len(self.bot.commands))
        embed.add_field(name="» OS", value=platform.system())
        embed.add_field(name="» Python Version", value=platform.python_version())
        embed.add_field(name="» Library", value=f"Discord.py: {discord.__version__}\n")
        embed.add_field(
            name="» Memory Usage",
            value=f"{float(process.memory_info().rss) / 1024 / 1024:0.2f} MB",
        )
        embed.add_field(name="» Developer", value="Runew0lf#0001")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
    log.info("Cog loaded: General")
