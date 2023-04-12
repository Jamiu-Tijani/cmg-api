from instagrapi import Client
from .scraper import scrape_latest_video

class InstagramService:
    def __init__(self):
    
        self.cl = Client()
        self.cl.login("cmg_the_label_", "@cmgthelabel4real")
    
    def get_stories(self, **kwargs):
        username = list(kwargs.get("username").split(","))
        cl = self.cl
        print(username)
        try:
            user_stories = {}
            for user in username:
                user_id = cl.user_id_from_username(user)
                try:
                    s = cl.user_stories(user_id)
                    user_stories.update({user:dict(s)})
                except:
                    user_stories.update({user:None})

            return dict(success="User stories fetch successful", status=200, data=user_stories)
        except Exception as error:
            print(error)
            return dict(error=str(error),status=404)

    def get_recent_post(self, **kwargs):
        username = list(kwargs.get("username").split(","))
        cl = self.cl
        print(username)
        try:
            data={}
            for user in username:
                user_id = cl.user_id_from_username(user)
                print(user_id)

                user_media = cl.user_medias_v1(user_id= user_id, amount= 3)
                print(user_media)
                if len(user_media) > 0:
                    data.update({user:user_media[0]})
                else:
                    data.update({user:404})
            return dict(success="User stories fetch successful", status=200, data=data)

        except Exception as error:
            print(error)
            return dict(error=str(error),status=500)

class TikTokService:
    def get_latest_feed(**kwargs):
        username = list(kwargs.get("username").split(","))
        data = {}
        for user in username:
            response = scrape_latest_video(username=user)
            data.update(response["data"])
        return dict(success="User stories fetch successful", status=200, data=data)
        

