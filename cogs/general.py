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

    @commands.command(name="1")
    async def info1(self, ctx):
        """
        Test Command 1
        """
        print("1")

    @commands.command(name="2")
    async def info2(self, ctx):
        """
        Test Command 2
        """
        print("2")

    @commands.command(name="3")
    async def info3(self, ctx):
        """
        Test Command 3
        """
        print("3")

    @commands.command(name="4")
    async def info4(self, ctx):
        """
        Test Command 4
        """
        print("4")

    @commands.command(name="5")
    async def info5(self, ctx):
        """
        Test Command 5
        """
        print("5")

    @commands.command(name="6")
    async def info6(self, ctx):
        """
        Test Command 6
        """
        print("6")

    @commands.command(name="7")
    async def info7(self, ctx):
        """
        Test Command 7
        """
        print("7")

    @commands.command(name="8")
    async def info8(self, ctx):
        """
        Test Command 8
        """
        print("8")

    @commands.command(name="9")
    async def info9(self, ctx):
        """
        Test Command 9
        """
        print("9")

    @commands.command(name="10")
    async def info10(self, ctx):
        """
        Test Command 10
        """
        print("10")


def setup(bot):
    bot.add_cog(General(bot))
    log.info("Cog loaded: General")
