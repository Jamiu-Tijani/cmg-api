import requests


class InstagramApi:
    def __init__(self):
        self.base_url = "https://instagram-scraper-2022.p.rapidapi.com/"
        self.headers = {
            "X-RapidAPI-Key": "2e67a84087msh613d317044d30e1p18e915jsn423d57b0ec95",
            "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com",
        }

    def get_user_posts(self, username):
        url = self.base_url + "ig/posts_username/"
        params = {"user": username}
        response = requests.request("GET", url, headers=self.headers, params=params)
        if response.status_code != 200:
            return dict(error="User not found", status=404, data=data)

        return dict(
            message="User latest feed fetch successful",
            status=200,
            data=response.json(),
        )

    def get_user_stories(self, username):
        url = self.base_url + "ig/user_id/"
        params = {"user": username}
        response = requests.request("GET", url, headers=self.headers, params=params)
        data = {username: None}
        if response.status_code != 200:
            return dict(error="User not found", status=404, data=data)
        user_id = response.json()["id"]
        stories_url = self.base_url + "ig/stories/"
        stories = requests.request(
            "GET", stories_url, headers=self.headers, params={"id_user": user_id}
        )
        if stories.status_code != 200:
            return dict(error="User not found", status=404, data=data)
        return dict(
            message="User latest feed fetch successful", status=200, data=stories.json()
        )


class TwitterApi:
    def __init__(self):
        self.base_url = "https://twitter135.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": "2e67a84087msh613d317044d30e1p18e915jsn423d57b0ec95",
            "X-RapidAPI-Host": "twitter135.p.rapidapi.com",
        }

    def get_user_profile_(self, username):
        url = self.base_url + "/UserByScreenName/"
        data = {username: None}
        querystring = {"username": username}
        response = requests.request(
            "GET", url, headers=self.headers, params=querystring
        )
        if response.status_code != 200:
            return dict(error="User not found", status=404, data=data)
        user_details = {}
        user_details["user_id"] = response.json()["data"]["user"]["result"]["rest_id"]
        user_details.update(response.json()["data"]["user"]["result"]["legacy"])
        return dict(
            message="User profile fetch successful", status=200, data=user_details
        )

    def get_user_tweets(self, username):
        user_profile = self.get_user_profile_(username)
        if user_profile["status"] != 200:
            return user_profile
        user_details = user_profile["data"]
        url = self.base_url + "/UserTweets/"
        querystring = {"id": user_details["user_id"], "count": "10"}
        response = requests.request(
            "GET", url, headers=self.headers, params=querystring
        )
        if response.status_code != 200:
            return dict(error="User data not found", status=404, data=data)

        user_profile_tweets = response.json()
        user_profile_tweets["user_profile"] = user_details
        return dict(
            message="User profile fetch successful",
            status=200,
            data=user_profile_tweets,
        )
