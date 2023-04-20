from bs4 import BeautifulSoup as bs
import requests


def scrape_latest_video(username):
    url = "https://www.tiktok.com/@" + username
    response = requests.get(url)
    if response.status_code == 404:
        data = {username: 404}
        return dict(error="User not found", status=404, data=data)
    soup = bs(response.text, "html.parser")
    video_urls = [x.get("href") for x in soup.findAll("a", {"tabindex": "-1"})[:10]]
    user_latest_feed = []
    for video_url in video_urls:
        data = {username: {"video_url": video_url}}
        video_response = requests.get(video_url)
        video_soup = bs(video_response.text, "html.parser")
        data[username]["video_author_comment"] = video_soup.find("span",{"class":"tiktok-j2a19r-SpanText efbd9f0"}).text.strip()
        for data_ in video_soup.findAll(
            "strong", {"class": "tiktok-cpjh4r-StrongText edu4zum2"}
        ):
            data[username][data_.get("data-e2e")] = data_.text
        data["followers_count"] = soup.find("strong",{"title":"Followers"}).text
        data["total_user_likes"] = soup.find("strong",{"title":"Likes"}).text
        data["following_count"] =soup.find("strong",{"title":"Following"}).text
        data["user_profile_pic"] = soup.find("img",{"class":"tiktok-1zpj2q-ImgAvatar e1e9er4e1"}).get("src")
        data["verified_status"] = False if soup.find("circle",{"fill":"#20D5EC"}) == None else True
        res = requests.get(f"https://api.douyin.wtf/tiktok_video_data/?tiktok_video_url={video_url}")
        try:
            for x in res.json()["aweme_list"]:
                if "video" in x:
                    data[username]["video_url"] = x["video"]["play_addr"]["url_list"][0]
        except Exception as error:
            print(error)    
        user_latest_feed.append(data)
            
    return dict(
        message="User latest feed fetch successful", status=200, data=user_latest_feed
    )
