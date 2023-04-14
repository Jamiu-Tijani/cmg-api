from instagrapi import Client
from .scraper import scrape_latest_video
from .rapidapi import InstagramApi, TwitterApi


class InstagramService:
    def __init__(self):
        self.s = ""

    def get_stories(self, **kwargs):
        username = list(kwargs.get("username").split(","))
        try:
            user_stories = {}
            for user in username:
                try:
                    s = InstagramApi().get_user_stories(username=user)["data"]
                    user_stories.update({user: dict(s)})
                except:
                    user_stories.update({user: None})
            return dict(
                success="User stories fetch successful", status=200, data=user_stories
            )
        except Exception as error:
            print(error)
            return dict(error=str(error), status=404)

    def get_recent_post(self, **kwargs):
        username = list(kwargs.get("username").split(","))
        try:
            data = {}
            for user in username:
                user_media = InstagramApi().get_user_posts(username=user)["data"]
                data.update({user: user_media})
            return dict(success="User stories fetch successful", status=200, data=data)

        except Exception as error:
            print(error)
            return dict(error=str(error), status=500)


class TikTokService:
    def get_latest_feed(**kwargs):
        username = list(kwargs.get("username").split(","))
        data = {}
        for user in username:
            response = scrape_latest_video(username=user)
            data.update(response["data"])
        return dict(success="User stories fetch successful", status=200, data=data)


class TwitterService:
    def get_user_tweets(**kwargs):
        username = list(kwargs.get("username").split(","))
        data = {}
        for user in username:
            response = TwitterApi().get_user_tweets(username=user)
            data.update(response["data"])
        return dict(success="User stories fetch successful", status=200, data=data)
