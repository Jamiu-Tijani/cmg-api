from instagrapi import Client


class InstagramService:
    def __init__(self):
    
        self.cl = Client()
        self.cl.login("cmg_the_label_", "@cmgthelabel4real")
    
    def get_socials(self, **kwargs):
        username = kwargs.get("username")
        user_id = cl.user_id_from_username("yogotti")
        s = cl.user_stories(user_id)

        return dict(success="User stories fetch successful", status=200, data=dict(s))
