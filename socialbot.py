import traceback
from os import listdir
from os.path import isfile, join

import discord
import discord.ext.commands.view
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils import pyson

cogs_dir = "cogs"
ignored_cogs = ["help"]


def get_prefix(client, message):
    prefix = bot.config.data.get("servers").get(str(message.guild.id)).get("prefix")
    if not prefix:
        prefix = "."
    return commands.when_mentioned_or(prefix)(bot, message)


bot = AutoShardedBot(command_prefix=get_prefix)

if __name__ == "__main__":
    for extension in [
        f.replace(".py", "") for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))
    ]:
        try:
            if extension != "__init__" and extension not in ignored_cogs:
                bot.load_extension(cogs_dir + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f"Failed to load extension {extension}.")
            traceback.print_exc()


@bot.event
async def on_ready():
    log.info(f"Logged in as: {bot.user.name} - {bot.user.id}")
    log.info(f"Version: {discord.__version__}\n")
    for guild in bot.guilds:
        log.info(f"Connected to server: {guild.name}")
        if not bot.config.data.get("servers").get(str(guild.id)):
            new_guild = {"prefix": "!"}
            bot.config.data["servers"][str(guild.id)] = new_guild
            bot.config.save()

    await bot.change_presence(activity=discord.Game(name="Testing"))


@bot.event
async def on_guild_join(guild):
    new_guild = {"prefix": "."}
    bot.config.data["servers"][str(guild.id)] = new_guild
    bot.config.save()


@bot.event
async def on_guild_remove(guild):
    bot.config.data["servers"].pop(str(guild.id), None)
    bot.config.save()


bot.config = pyson.Pyson("cogs/config/config.json")
token = bot.config.data.get("config").get("token")
bot.run(token, bot=True, reconnect=True)
