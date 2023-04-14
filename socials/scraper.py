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
    return dict(
        message="User latest feed fetch successful", status=200, data=user_latest_feed
    )
