import json

import feedparser
import praw
import requests
import twitch
import twitter
import discord
from discord.ext import commands, tasks
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils import checks
from cogs.utils.instagram import InstagramScraper


emoji_list = [
    "<:youtube:598977459622248651>",
    "<:twitter:598977459353944121>",
    "<:twitch:598977459173720064>",
    "<:reddit:598977459177914368>",
    "<:mixer:598977459085639687>",
    "<:instagram:598978116404248693>"
]
role_list = [
    "Youtube",
    "Twitter",
    "Twitch",
    "Reddit",
    "Mixer",
    "Instagram"
]

class Social(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        with open("cogs\\config\\data.json") as fh:
            self.data = json.load(fh)

        # self.data = {
        #     "598524730206846977":
        #     {
        #         "channel_id": 598803745672790016,
        #         "social": {
        #             "twitter": {"username": "runew0lf", "last_post": None},
        #             "instagram": {"username": "runew0lf", "last_post": None},
        #             "twitch": {"username": "runew0lf", "live": False},
        #             "mixer": {"username": "runew0lf", "live": False},
        #             "youtube": {"username": "runew0lf", "last_post": False},
        #             "reddit": {"username": "runew0lf", "last_post": False},
        #         },
        #     },
        # }

    @commands.Cog.listener()
    async def on_ready(self):
        self.check.start()

    @tasks.loop(seconds=120)
    async def check(self):
        for key in self.data:
            server = self.data[key]
            channel = self.bot.get_channel(server["channel_id"])

            # Check Twitter
            username = server["social"]["twitter"]["username"]
            twitter_check = self.get_twitter(username)
            if server["social"]["twitter"]["last_post"] != twitter_check:
                role = discord.utils.get(channel.guild.roles, name="Twitter")
                await channel.send(role.mention)
                await channel.send(
                    f"https://twitter.com/{username}/status/{twitter_check}"
                )
                server["social"]["twitter"]["last_post"] = twitter_check

            # Check Instagram
            username = server["social"]["instagram"]["username"]
            insta_check = self.get_instagram(username)
            if server["social"]["instagram"]["last_post"] != insta_check["shortcode"]:
                server["social"]["instagram"]["last_post"] = insta_check["shortcode"]
                text = insta_check["edge_media_to_caption"]["edges"][0]["node"]["text"]
                role = discord.utils.get(channel.guild.roles, name="Instagram")
                await channel.send(role.mention)
                await channel.send(
                    f"https://www.instagram.com/p/{insta_check['shortcode']}/"
                )
                await channel.send(f"`{text}`")

            # Check Reddit
            username = server["social"]["reddit"]["username"]
            reddit_check = self.get_reddit(username)
            if server["social"]["reddit"]["last_post"] != reddit_check.id:
                server["social"]["reddit"]["last_post"] = reddit_check.id
                role = discord.utils.get(channel.guild.roles, name="Reddit")
                await channel.send(role.mention)
                await channel.send(reddit_check.link_permalink)
                await channel.send(reddit_check.body)

            # Check Youtube
            username = server["social"]["youtube"]["username"]
            youtube_check = self.get_youtube(username)
            if server["social"]["youtube"]["last_post"] != youtube_check:
                server["social"]["youtube"]["last_post"] = youtube_check
                role = discord.utils.get(channel.guild.roles, name="Youtube")
                await channel.send(role.mention)
                await channel.send(f"https://www.youtube.com/watch?v={youtube_check}")

            # Check twitch
            username = server["social"]["twitch"]["username"]
            twitch_check = self.get_twitch(username)
            if server["social"]["twitch"]["live"] != twitch_check:
                server["social"]["twitch"]["live"] = twitch_check
                if twitch_check:
                    twitch_id = self.bot.config.data.get("config").get(
                        "TWITCH_CLIENT_ID"
                    )
                    helix = twitch.Helix(twitch_id)
                    game_id = helix.user(username).stream().game_id
                    title = helix.user(username).stream().title
                    game = helix.game(id=game_id)
                    role = discord.utils.get(channel.guild.roles, name="Twitch")
                    await channel.send(role.mention)
                    await channel.send("Stream is now live!")
                    await channel.send(f"<https://twitch.tv/{username}>")
                    await channel.send(f"Title: {title}")
                    await channel.send(f"Streaming: {game.name}")
                else:
                    await channel.send("Stream has gone offline")

            # Check mixer
            username = server["social"]["mixer"]["username"]
            mixer_check = self.get_mixer(username)
            if server["social"]["mixer"]["live"] != mixer_check:
                server["social"]["mixer"]["live"] = mixer_check
                if mixer_check:
                    data = requests.get(
                        f"https://mixer.com/api/v1/channels/{username}?fields=online,name,type"
                    ).json()
                    role = discord.utils.get(channel.guild.roles, name="Mixer")
                    await channel.send(role.mention)
                    await channel.send("Stream is now live!")
                    await channel.send(f"<https://mixer.com/{username}>")
                    await channel.send(f"Title: {data['name']}")
                    await channel.send(f"Streaming: {data['type']['name']}")
                else:
                    await channel.send("Stream has gone offline")

            with open("cogs\\config\\data.json", "w") as fh:
                json.dump(self.data, fh, indent=4)

    def get_twitter(self, username):
        if username is not None:
            api = twitter.Api(
                consumer_key=self.bot.config.data.get("config").get("CONSUMER_KEY"),
                consumer_secret=self.bot.config.data.get("config").get(
                    "CONSUMER_SECRET"
                ),
                access_token_key=self.bot.config.data.get("config").get("ACCESS_TOKEN"),
                access_token_secret=self.bot.config.data.get("config").get(
                    "ACCESS_TOKEN_SECRET"
                ),
            )
            statuses = api.GetUserTimeline(screen_name=f"@{username}")
            for tweet in statuses:
                if tweet.in_reply_to_status_id is None:
                    return tweet.id

    def get_instagram(self, username):
        k = InstagramScraper()
        results = k.profile_page_recent_posts(
            f"https://www.instagram.com/{username}/?hl=en"
        )
        return results[0]

    def get_reddit(self, user):
        client_id = self.bot.config.data.get("config").get("REDDIT_ID")
        client_secret = self.bot.config.data.get("config").get("REDDIT_SECRET")
        user_agent = self.bot.config.data.get("config").get("REDDIT_AGENT")
        reddit_client = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )

        for comment in reddit_client.redditor(user).comments.new(limit=1):
            return comment

    def get_youtube(self, user):
        d = feedparser.parse(f"https://www.youtube.com/feeds/videos.xml?user={user}")
        video_id = d["entries"][0]["yt_videoid"]
        return video_id

    def get_twitch(self, user):
        twitch_id = self.bot.config.data.get("config").get("TWITCH_CLIENT_ID")
        helix = twitch.Helix(twitch_id)
        live_flag = False
        try:
            helix.user(user).stream().type
            live_flag = True
        except twitch.helix.streams.StreamNotFound:
            live_flag = False
        return live_flag

    def get_mixer(self, user):
        data = requests.get(
            f"https://mixer.com/api/v1/channels/{user}?fields=online"
        ).json()
        return data["online"]

    @commands.command(name="instagram", aliases=["ig"])
    async def instagram(self, ctx, ig_name="runew0lf"):
        results = self.get_instagram(ig_name)
        shortcode = results["shortcode"]
        text = results["edge_media_to_caption"]["edges"][0]["node"]["text"]
        await ctx.send(f"https://www.instagram.com/p/{shortcode}/")
        await ctx.send(f"`{text}`")

    @commands.command(name="twitter", aliases=["tweet"])
    async def twit(self, ctx, username: str = "runew0lf"):
        await ctx.send(
            f"https://twitter.com/{username}/status/{self.get_twitter(username)}"
        )

    @commands.command(name="twitch", aliases=["tw"])
    async def twitch(self, ctx, user="runew0lf"):
        twitch_id = self.bot.config.data.get("config").get("TWITCH_CLIENT_ID")
        helix = twitch.Helix(twitch_id)
        try:
            await ctx.send(helix.user(user).stream().type)
            game_id = helix.user(user).stream().game_id
            title = helix.user(user).stream().title
            test = helix.game(id=game_id)
            await ctx.send(f"<https://twitch.tv/{user}>")
            await ctx.send(f"Title: {title}")
            await ctx.send(f"Streaming: {test.name}")
        except twitch.helix.streams.StreamNotFound:
            await ctx.send("Not Live")

    @commands.command(name="youtube", aliases=["yt"])
    async def youtube(self, ctx, user="runew0lf"):
        video_id = self.get_youtube(user)
        await ctx.send(f"https://www.youtube.com/watch?v={video_id}")

    @commands.command(name="mixer")
    async def mixer(self, ctx, user="runew0lf"):
        if self.get_mixer(user):
            await ctx.send("Live")
        else:
            await ctx.send("Not Live")

    @commands.command(name="reddit")
    async def reddit(self, ctx, user="runew0lf"):
        comment = self.get_reddit(user)
        await ctx.send(comment.link_permalink)
        await ctx.send(comment.body)

    @commands.command(name="setup")
    @checks.is_admin()
    async def setup_data(self, ctx):
        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(
            "Would you like to setup a notification subscription channel? (yes or no)"
        )
        msg = await self.bot.wait_for("message", check=check)
        if msg.content == "yes":
            await ctx.send("Sure let me get that setup for you")
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(send_messages=True)
            }            
            channel = await ctx.guild.create_text_channel("Notification-Subscription", overwrites=overwrites)
            message = await channel.send(
                "To subcribe to notifications, simply click the below buttons to start"
            )
            # add our reactions to the message
            for emoji in emoji_list:
                await message.add_reaction(emoji)
            await ctx.send("Channel Created")
            for role in role_list:
                await ctx.guild.create_role(name=role, mentionable=True)
            await ctx.send("Roles Created")
            self.data[str(ctx.guild.id)]["notification_id"] = message.id
            with open("cogs\\config\\data.json", "w") as fh:
                json.dump(self.data, fh, indent=4)            
        else:
            await ctx.send("Ok, no notification channel")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message_id = payload.message_id
        if message_id != self.data[str(payload.guild_id)]["notification_id"]:
            return
        user = self.bot.get_user(payload.user_id)
        if user.bot:
            return
        member = channel.guild.get_member(payload.user_id)
        emoji = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        if emoji in emoji_list:
            index = emoji_list.index(emoji)
            role_name = role_list[index]
            role = discord.utils.get(channel.guild.roles, name=role_name)
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message_id = payload.message_id
        if message_id != self.data[str(payload.guild_id)]["notification_id"]:
            return
        user = self.bot.get_user(payload.user_id)
        if user.bot:
            return
        member = channel.guild.get_member(payload.user_id)
        emoji = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        if emoji in emoji_list:
            index = emoji_list.index(emoji)
            role_name = role_list[index]
            role = discord.utils.get(channel.guild.roles, name=role_name)
            await member.remove_roles(role)


def setup(bot):
    bot.add_cog(Social(bot))
    log.info("Cog loaded: Social")

