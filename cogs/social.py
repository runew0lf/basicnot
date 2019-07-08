import praw
import requests
import twitch
import twitter
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from loguru import logger as log

from cogs.utils.instagram import InstagramScraper


class Social(commands.Cog):
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.command(name="instagram", aliases=["ig"])
    async def instagram(self, ctx, ig_name="runew0lf"):
        k = InstagramScraper()
        results = k.profile_page_recent_posts(f'https://www.instagram.com/{ig_name}/?hl=en')
        url = f"https://www.instagram.com/p/{results[0]['shortcode']}/"
        text = results[0]['edge_media_to_caption']['edges'][0]['node']['text']
        await ctx.send(url)
        await ctx.send(f"`{text}`")

    @commands.command(name='twitter', aliases=['tweet'])
    async def twit(self, ctx, username: str = "runew0lf"):
        """
        Gets the users latest tweets
        Usage: !twitter <username>
        """
        if username is not None:
            api = twitter.Api(
                consumer_key=self.bot.config.data.get("config").get("CONSUMER_KEY"),
                consumer_secret=self.bot.config.data.get("config").get('CONSUMER_SECRET'),
                access_token_key=self.bot.config.data.get("config").get('ACCESS_TOKEN'),
                access_token_secret=self.bot.config.data.get("config").get('ACCESS_TOKEN_SECRET')
            )
            statuses = api.GetUserTimeline(screen_name=f"@{username}")
            for tweet in statuses:
                if tweet.in_reply_to_status_id is None:
                    await ctx.send(f"https://twitter.com/{username}/status/{tweet.id}")
                    return

    @commands.command(name="twitch", aliases=["tw"])
    async def twitch(self, ctx, user="runew0lf"):
        twitch_id = self.bot.config.data.get("config").get("TWITCH_CLIENT_ID")
        helix = twitch.Helix(twitch_id)
        try:
            await ctx.send(helix.user(user).stream().type)
        except twitch.helix.streams.StreamNotFound:
            await ctx.send("Not Live")

    @commands.command(name="youtube", aliases=["yt"])
    async def youtube(self, ctx, user="runew0lf"):
        yt_api = self.bot.config.data.get("config").get("YT_API")
        r = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&forUsername={user}&key={yt_api}")
        data = r.json()
        user_id = data['items'][0]['id']
        r = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={user_id}&maxResults=1&order=date&type=video&key={yt_api}")
        data = r.json()
        video_id = data['items'][0]['id']['videoId']
        await ctx.send(f"https://www.youtube.com/watch?v={video_id}")

    @commands.command(name="mixer")
    async def mixer(self, ctx, user="runew0lf"):
        data = requests.get(f"https://mixer.com/api/v1/channels/{user}?fields=online").json()
        if data['online'] is True:
            await ctx.send("Live")
        else:
            await ctx.send("Not Live")

    @commands.command(name="reddit")
    async def reddit(self, ctx, user="runew0lf"):
        client_id = self.bot.config.data.get("config").get("REDDIT_ID")
        client_secret = self.bot.config.data.get("config").get("REDDIT_SECRET")
        user_agent = self.bot.config.data.get("config").get("REDDIT_AGENT")
        reddit_client = praw.Reddit(client_id=client_id,
                                    client_secret=client_secret,
                                    user_agent=user_agent)

        for comment in reddit_client.redditor(user).comments.new(limit=1):
            print(dir(comment))
            await ctx.send(comment.link_permalink)
            await ctx.send(comment.body)

def setup(bot):
    bot.add_cog(Social(bot))
    log.info("Cog loaded: Social")
