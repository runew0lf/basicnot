from discord.ext import commands


def is_admin():
    async def predicate(ctx):
        permissions = ctx.channel.permissions_for(ctx.author)
        return permissions.administrator
    return commands.check(predicate)


def is_guild_owner():
    async def predictate(ctx):
        if ctx.author is ctx.guild.owner:
            return True
        return False
    return commands.check(predictate)