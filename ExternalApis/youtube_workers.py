from os import stat
from aiohttp import ClientSession, TCPConnector
from aiohttp.client_exceptions import ClientOSError
from redis.commands.core import ResponseT
from StarlordYouTube import YoutubeApi
from rawg import rawg_genre_endpoint
import aiohttp
import asyncio
from typing import List
import redis

yt = YoutubeApi()
base_url = "http://localhost:5500/"
r = redis.Redis(
    host="redis-13909.c322.us-east-1-2.ec2.cloud.redislabs.com",
    port=13909,
    password="",
)

GAMES_QUEUE = "games:all"
YT_CHANNELS_QUEUE = "channels:all"
SPLATTERCAT_GAMES_NEXTPAGE_TOKEN = "next_page_token:splattercatgaming"


# GETS AND SAVES INDIE GAMES PLAYED BY SPLATTERCAT THE OG :)
async def worker_get_all_games_by_splatter_cat():
    channel_id = yt.get_channel_id_by_name("splattercatgaming")
    # channel_id = yt.get_channel_id_by_name("wanderbots")

    # get the next page
    token: ResponseT | None = r.get(SPLATTERCAT_GAMES_NEXTPAGE_TOKEN)
    results, next_page_token = yt.most_popular_or_recent_video(
        channel_id, order=1, next_page_token=token
    )
    r.set(SPLATTERCAT_GAMES_NEXTPAGE_TOKEN, str(next_page_token))
    video_ids: List[str] = [x[0] for x in results]
    games_played = map(yt.games_played_and_linked_details, video_ids)
    games_played = [video[0] for video in list(games_played) if video[0]]
    games_and_genres_to_add = []
    for g in games_played:
        data = rawg_genre_endpoint(g)
        if data:
            genres_ = "#".join(data)
            games_and_genres_to_add.append(g + "@" + genres_)
    # save the games games_played to redis list
    r.rpush(GAMES_QUEUE, *games_and_genres_to_add)


# POPS THE GAMES QUEUE AND SEARCHES FOR CHANNELS PLAYING THE GAMES PROPOSED
async def worker_yt_search_for_indie_playing_channels():
    game_and_genre = r.rpop(GAMES_QUEUE)
    if game_and_genre == None:
        return
    game_and_genre = game_and_genre.decode("utf-8")
    game_and_genre = game_and_genre.split("@")
    game = game_and_genre[0]
    genres = None
    if len(game_and_genre) > 1:
        genres = game_and_genre[1]

    search_data, _ = yt.search_particular_indie_gameplay_channels(game_name=str(game))
    list_of_channel_ids = []
    for _, val in search_data.items():
        channel_id, _ = val[0]["channel_id"], val[0]["description"]
        list_of_channel_ids.append(channel_id + "@" + genres)

    r.rpush(YT_CHANNELS_QUEUE, *list_of_channel_ids)


async def worker_yt_add_channels_to_db():
    channel_ids_and_genres = r.rpop(YT_CHANNELS_QUEUE, count=50)
    if channel_ids_and_genres == None:
        return
    channel_ids = [ch.decode("utf-8").split("@")[0] for ch in channel_ids_and_genres]
    genres = [
        ch.decode("utf-8").split("@")[1].split("#") for ch in channel_ids_and_genres
    ]

    url = base_url + "api/get_streamer"
    headers = {"Content-Type": "application/json"}
    connector = TCPConnector(limit=100)  # Reuse connections
    async with aiohttp.ClientSession(connector=connector) as Session:
        data_to_send = []
        for index, ch in enumerate(set(channel_ids)):
            data = {"channel_id": ch}
            exists = False
            try:
                async with Session.get(
                    url, json=data, headers=headers, timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("API RESPONSE: ", result)
                        exists = result.get("exists", False)
            except (ClientOSError, asyncio.TimeoutError) as e:
                print(f"Error occurred: {e}")
                # Handle error or retry
            if not exists:
                data_to_send.append(add_streamer(ch, genres[index]))

        url_p = base_url + "create_streamer/"
        for d in data_to_send:
            async with Session.post(
                url=url_p, json=d, headers=headers, timeout=10
            ) as response:
                if response.status == 200:
                    print("done")
                else:
                    print(f"Error while posting to {url_p}")


async def yt_worker_update_streamer_video_history():
    url = base_url + "api/api_get_streamer_paginated"
    result = {}
    connector = TCPConnector(limit=1000)  # Reuse connections
    async with aiohttp.ClientSession(connector=connector) as Session:
        result = await get_paginated_result(Session, url)

    if not result["streamers"]:
        return
    data = [(r[0], r[-5]) for r in result["streamers"]]
    result.clear()

    request_data = [fetch_most_poupular_video(ch) for ch in data]

    post_url = base_url + "/api/update_streamer_videos/"

    connector = TCPConnector(limit=1000)  # Reuse connections
    async with aiohttp.ClientSession(connector=connector) as Session:
        for d in request_data:
            await update_videos(post_url, Session, d)


async def get_paginated_result(Session: ClientSession, url):
    async with Session.get(url) as response:
        if response.status == 200:
            result = await response.json()
            return result
        else:
            return {"streamers": []}


async def update_videos(post_url: str, Session: ClientSession, data):
    async with Session.post(post_url, json=data) as response:
        if response.status == 200:
            pass
        else:
            print("Error in post")


def fetch_most_poupular_video(ch):
    vids = YoutubeApi().most_popular_or_recent_video(channel_id=ch[1])
    vids = vids[0]
    return generate_video_data(ch[0], vids)


def generate_video_data(db_id: int, videos: List[list]):
    data = {"id": db_id, "videos": []}
    for video in videos:
        statistics = video[-1]["statistics"]
        stat = {
            "views": int(statistics["viewCount"]) if "viewCount" in statistics else 0,
            "comments": (
                int(statistics["commentCount"]) if "commentCount" in statistics else 0
            ),
            "likes": int(statistics["likeCount"]) if "likeCount" in statistics else 0,
            "upload_date": "1988-01-17",
        }
        data["videos"].append(stat)
    return data


def add_streamer(channel_id, genres: List[str]):
    data = {
        "name": "",
        "email": "",
        "twitter": "",
        "twitter_followers": 0,
        "instagram": "",
        "instagram_followers": 0,
        "twitch_url": "",
        "twitch_subs": 0,
        "youtube_url": None,
        "youtube_subs": 0,
        "country": "",
        "genres": [],
    }
    stats = yt.channel_statistics(channel_id)
    data["youtube_subs"] = int(stats[channel_id]["youtube_subscribers"])
    data["youtube_url"] = channel_id
    data["country"] = stats[channel_id]["country"]
    data["genres"] = genres
    description = stats[channel_id]["description"]
    email = yt.emailFinder(description)
    if email:
        data["email"] = email[0]

    socials = yt.scrape_social_media(channel_id)
    if socials:
        if socials["Twitch"]:
            twitch_username = socials["Twitch"].split("2F")[1]
            data["twitch_url"] = twitch_username
        if socials["Twitter"]:
            twitter_username = socials["Twitter"].split("2F")[1]
            data["twitter"] = twitter_username
        if socials["Instagram"]:
            instagram_username = socials["Instagram"].split("2F")[1]
            data["instagram"] = instagram_username
    data["name"] = yt.get_channel_name(channel_id)
    return data


async def create_single_streamer(name="splattercatgaming"):
    url = base_url + "api/get_streamer"
    data = {"name": name}
    headers = {"Content-Type": "application/json"}
    exists = False
    channel_id = yt.get_channel_id_by_name(name)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, json=data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                exists = result["exists"]
            else:
                pass
                # print(f"Error: {response.status}")
    if not exists:
        url = base_url + "create_streamer/"
        data = {
            "name": name,
            "email": "",
            "twitter": "",
            "twitter_followers": 0,
            "instagram": "",
            "instagram_followers": 0,
            "twitch_url": "",
            "twitch_subs": 0,
            "youtube_url": None,
            "youtube_subs": 0,
            "country": "",
            "genres": [],
        }
        stats = yt.channel_statistics(channel_id)
        data["youtube_subs"] = int(stats[channel_id]["youtube_subscribers"])
        data["youtube_url"] = channel_id
        description = stats[channel_id]["description"]
        email = yt.emailFinder(description)
        if email:
            data["email"] = email[0]

        socials = yt.scrape_social_media(channel_id)
        if socials:
            if socials["Twitch"]:
                twitch_username = socials["Twitch"].split("2F")[1]
                data["twitch_url"] = twitch_username
            if socials["Twitter"]:
                twitter_username = socials["Twitter"].split("2F")[1]
                data["twitter"] = twitter_username
            if socials["Instagram"]:
                instagram_username = socials["Instagram"].split("2F")[1]
                data["instagram"] = instagram_username


loop = asyncio.get_event_loop()
loop.run_until_complete(worker_get_all_games_by_splatter_cat())
loop.run_until_complete(worker_yt_search_for_indie_playing_channels())
loop.run_until_complete(worker_yt_add_channels_to_db())
# loop.run_until_complete(yt_worker_update_streamer_video_history())
