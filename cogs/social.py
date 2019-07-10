import praw
import requests
import twitch
import twitter
from discord.ext import commands, tasks
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils.instagram import InstagramScraper

TEST_CHANNEL = 492439189590114332


class Social(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.data = {"twitter":
                     {
                        "username": "runew0lf",
                        "last_post": None
                     },
                     "instagram":
                     {
                         "username": "runew0lf",
                         "last_post": None

                     },
                     "twitch":
                     {
                         "username": "runew0lf",
                         "live": False
                     }
                     }

    @commands.Cog.listener()
    async def on_ready(self):
        self.check.start()

    @tasks.loop(seconds=10)
    async def check(self):
        channel = self.bot.get_channel(TEST_CHANNEL)
        # Check Twitter
        username = self.data['twitter']['username']
        twitter_check = self.get_twitter(username)
        if self.data['twitter']['last_post'] != twitter_check:
            await channel.send(f"https://twitter.com/{username}/status/{twitter_check}")
            self.data['twitter']['last_post'] = twitter_check
        # Check Instagram
        username = self.data['instagram']['username']
        insta_check = self.get_instagram(username)
        
        if self.data['instagram']['last_post'] != insta_check['shortcode']:
            self.data['instagram']['last_post'] = insta_check['shortcode']
            text = insta_check["edge_media_to_caption"]["edges"][0]["node"]["text"]
            await channel.send(f"https://www.instagram.com/p/{insta_check['shortcode']}/")
            await channel.send(f"`{text}`")
        #Check Reddit


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

    @commands.command(name="instagram", aliases=["ig"])
    async def instagram(self, ctx, ig_name="runew0lf"):
        results = self.get_instagram(ig_name)
        shortcode = results['shortcode']
        text = results["edge_media_to_caption"]["edges"][0]["node"]["text"]
        await ctx.send(f"https://www.instagram.com/p/{shortcode}/")
        await ctx.send(f"`{text}`")

    @commands.command(name="twitter", aliases=["tweet"])
    async def twit(self, ctx, username: str = "runew0lf"):
        await ctx.send(f"https://twitter.com/{username}/status/{self.get_twitter(username)}")

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
        yt_api = self.bot.config.data.get("config").get("YT_API")
        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername={user}&key={yt_api}"
        )
        data = r.json()
        user_id = data["items"][0]["id"]
        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={user_id}&maxResults=1&order=date&type=video&key={yt_api}"
        )
        data = r.json()
        video_id = data["items"][0]["id"]["videoId"]
        await ctx.send(f"https://www.youtube.com/watch?v={video_id}")

    @commands.command(name="mixer")
    async def mixer(self, ctx, user="runew0lf"):
        data = requests.get(
            f"https://mixer.com/api/v1/channels/{user}?fields=online"
        ).json()
        if data["online"] is True:
            await ctx.send("Live")
        else:
            await ctx.send("Not Live")

    @commands.command(name="reddit")
    async def reddit(self, ctx, user="runew0lf"):
        client_id = self.bot.config.data.get("config").get("REDDIT_ID")
        client_secret = self.bot.config.data.get("config").get("REDDIT_SECRET")
        user_agent = self.bot.config.data.get("config").get("REDDIT_AGENT")
        reddit_client = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )

        for comment in reddit_client.redditor(user).comments.new(limit=1):
            await ctx.send(comment.link_permalink)
            await ctx.send(comment.body)


def setup(bot):
    bot.add_cog(Social(bot))
    log.info("Cog loaded: Social")
