from bs4 import BeautifulSoup as bs
import requests


def scrape_latest_video(username):
    url = "https://www.tiktok.com/@" + username
    response = requests.get(url)
    if response.status_code == 404:
        data = {username: 404}
        return dict(error="User not found", status=404, data=data)
    soup = bs(response.text, "html.parser")
    video_url = soup.find("a", {"tabindex": "-1"}).get("href")
    video_response = requests.get(video_url)
    video_soup = bs(video_response.text, "html.parser")
    user_latest_feed = {username: {"video_url": video_url}}
    for data in video_soup.find_all(
        "strong", {"class": "tiktok-cpjh4r-StrongText edu4zum2"}
    ):
        user_latest_feed[username][data.get("data-e2e")] = data.text
    user_latest_feed["followers_count"] = soup.find("strong",{"title":"Followers"}).text
    user_latest_feed["total_user_likes"] = soup.find("strong",{"title":"Likes"}).text
    user_latest_feed["following_count"] =soup.find("strong",{"title":"Following"}).text
    user_latest_feed["user_profile_pic"] = soup.find("img",{"class":"tiktok-1zpj2q-ImgAvatar e1e9er4e1"}).get("src")
    user_latest_feed["verified_status"] = False if soup.find("circle",{"fill":"#20D5EC"}) == None else True
    res = requests.get(f"https://api.douyin.wtf/tiktok_video_data/?tiktok_video_url={video_url}")
    try:
        for x in res.json()["aweme_list"]:
            if "video" in x:
                user_latest_feed[username]["video_url"] = x["video"]["play_addr"]["url_list"][0]
    except Exception as error:
        print(error)        
    return dict(
        message="User latest feed fetch successful", status=200, data=user_latest_feed
    )
