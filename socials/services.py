from instagrapi import Client


class InstagramService:
    def __init__(self):
    
        self.cl = Client()
        self.cl.login("cmg_the_label_", "@cmgthelabel4real")
    
    def get_stories(self, **kwargs):
        username = kwargs.get("username")
        cl = self.cl
        try:
            user_id = cl.user_id_from_username(username)
            s = cl.user_stories(user_id)
            return dict(success="User stories fetch successful", status=200, data=dict(s))
        except Exception as error:
            return dict(error=str(error),status=404)

    def get_recent_post(self, **kwargs):
        username = kwargs.get("username")
        cl = self.cl
        try:
            user_id = cl.user_id_from_username(username)
            user_media = cl.user_medias_v1(user_id= user_id, amount= 3)
            if len(user_media) > 0:
                return dict(success="User stories fetch successful", status=200, data=dict(user_media[0]))
            else:
                return dict(success="User latest post not available", status=200, data=dict(user_media[0]))

        except Exception as error:
            return dict(error=str(error),status=404)