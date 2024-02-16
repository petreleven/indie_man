import requests
import pprint
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

BASE_URL = "https://id.twitch.tv/oauth2/token"
HEADERS = {"Client-ID": CLIENT_ID}
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
}
base_url = "https://api.twitch.tv/helix/games?name=Valorant"


def getGameID(game_name: str, headers: Dict[str, str]):
    base_url = f"https://api.twitch.tv/helix/games?name={game_name}"
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        game_id_data = data["data"]
        if len(game_id_data) > 0:
            game_id = game_id_data[0]["id"]
            return True, game_id

    print(f"Error in GETTING ID: {response.status_code} - {response.text}")
    return False, 0


def search(access_token, game_name, FIRST=10):
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {access_token}"}
    params = {"first": FIRST}

    # OBTAIN GAME ID
    status, game_id = getGameID(game_name, headers)

    if status:
        max_results = 1
        search_url = f"https://api.twitch.tv/helix/videos?game_id={game_id}&sort=views&first={max_results}"
        # OBTAIN VIDEO JSON DATA
        search_data = executeSearch(search_url, headers, game_id)
        # pprint.pprint(search_data)
        user_id = []
        for video in search_data:
            user_id.append(video["user_id"])
            view_count = video["view_count"]
            thumbnail_url = video["thumbnail_url"]

        for user in user_id:
            print("*" * 20)
            user_data = getTwitchStreamer(user, headers)
            pprint.pprint(user_data)


def getTwitchStreamer(id, headers):
    user_url = f"https://api.twitch.tv/helix/users?id={id}"
    response = requests.get(user_url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
        return data
    else:
        print(f"Error in getTwitchStreamer: {response.status_code} - {response.text}")


def executeSearch(search_url, headers, game_id):
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
        return data
    else:
        print(f"Error in executeSearch: {response.status_code} - {response.text}")


def getChannelStatSummary(channel_name: str):
    url = f"https://twitchtracker.com/api/channels/summary/{channel_name}"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data

    print("ERROR GETTING CHANNEL INFO")


"""Returns list of games played by a channel"""


def getGamesPlayedFromChannelClips(user_id: str, access_token):
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {access_token}"}
    # url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&first=4"
    url = f"https://api.twitch.tv/helix/clips?broadcaster_id={user_id}&first=20"
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
        games_played = []
        for clip in data:
            game_name = getGameFromID(game_id=clip["game_id"], headers=headers)
            if game_name != None:
                games_played.append(game_name)
        return games_played

    return "ERROR"


def getGameFromID(game_id: str, headers):
    url = f"https://api.twitch.tv/helix/games?id={game_id}"
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]
        if len(data) > 0:
            return data[0]["name"]
        return None
    return None


def getHTMLpanelContent(channel_name: str):
    session = requests_html.HTMLSession()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    response = session.get(f"https://www.twitch.tv/{channel_name}/about")
    if response.status_code == 200:
        pprint.pprint(response.text)


response = requests.post(BASE_URL, data=data)
if response.status_code == 200:
    print(response.json())
    access_token = response.json()["access_token"]
    # search(access_token, "Trash Goblin")
    # games_played = getGamesPlayedFromChannelClips(  user_id="43364473", access_token=access_token)
    # print(games_played)
    # getTwitchStreamer(id, headers)
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {access_token}"}
    user_data = getTwitchStreamer("43364473", headers=headers)
    name = user_data[0]["login"]
    stats = getChannelStatSummary("TheRealKnossi")
    print(stats)

else:
    print(f"ERROR in ACCESS TOKEN: {response.status_code} - {response.text}")


"""
search game 
get twitchstreeamer description ----DONE
get twitchstreamer email frrom desciption or scrape about page--- 1/2DONE
get twitchstreeamer games played and use rawg to get the genres played -- 1/2DONE
get twitch streamer other social links 
"""
