import requests


class InstagramApi:
    def __init__(self):
        self.base_url = "https://instagram-scraper-2022.p.rapidapi.com/"
        self.headers = {
            	"X-RapidAPI-Key": "2e67a84087msh613d317044d30e1p18e915jsn423d57b0ec95",
	"X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
        }


    def get_user_posts(self, username):
        url = self.base_url + "ig/posts_username/"
        params = {"user":username}
        response = requests.request("GET",url,headers=self.headers,params=params)
        if response.status_code != 200:
            return dict(error="User not found",status=404,data=data)

        return dict(message="User latest feed fetch successful",status=200,data=response.json())

    def get_user_stories(self, username):
        url = self.base_url + "ig/user_id/"
        params = {"user":username}
        response = requests.request("GET",url,headers=self.headers,params=params)
        if response.status_code != 200:
            return dict(error="User not found",status=404,data=data)
        user_id = response.json()["id"]
        stories_url = self.base_url + "ig/stories/"
        stories = requests.request("GET",stories_url,headers=self.headers,params={"id_user":user_id})
        if stories.status_code != 200:
            return dict(error="User not found",status=404,data=data)      
        return dict(message="User latest feed fetch successful",status=200,data=stories.json())