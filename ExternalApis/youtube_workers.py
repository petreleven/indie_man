from os import stat
from pprint import pprint

from redis.commands.core import ResponseT
from StarlordYouTube import YoutubeApi
import aiohttp
import asyncio
from typing import List
import redis
yt = YoutubeApi()
base_url = "http://localhost:5500/"
r = redis.Redis(
      host='redis-13909.c322.us-east-1-2.ec2.cloud.redislabs.com',
      port=13909,
      password='zHM90rc6O2GB0Qv57z4GZhvaLNyUUFjR')
GAMES_QUEUE = "games:all"
YT_CHANNELS_QUEUE= ""
SPLATTERCAT_GAMES_NEXTPAGE_TOKEN = "next_page_token:splattercatgaming"


#GETS AND SAVES INDIE GAMES PLAYED BY SPLATTERCAT THE OG :)
async def worker_get_all_games_by_splatter_cat():
    channel_id = yt.get_channel_id_by_name("splattercatgaming")
    #get the next page
    token : ResponseT | None = r.get(SPLATTERCAT_GAMES_NEXTPAGE_TOKEN)
    results, next_page_token = yt.most_popular_or_recent_video(channel_id, 
                                                               order=1,
                                                               next_page_token=str(token))
    r.set(SPLATTERCAT_GAMES_NEXTPAGE_TOKEN, str(next_page_token))
    video_ids : List[str] = [x[0] for x in results]
    games_played = map(yt.games_played_and_linked_details,video_ids)
    games_played = [video[0] for video in list(games_played) if video[0]]
    #save the games games_played to redis list
    r.rpush(GAMES_QUEUE, *games_played)


#POPS THE GAMES QUEUE AND SEARCHES FOR CHANNELS PLAYING THE GAMES PROPOSED
#
async def worker_yt_search_for_indie_playing_channels():
    game = r.rpop(GAMES_QUEUE)
    if game==None:
        return

    search_data, _ = yt.search_particular_indie_gameplay_channels(
        game_name=str(game))
    list_of_channel_ids = []
    for _, val in search_data.items():
        channel_id, _ = val[0]["channel_id"], val[0]["description"]
        list_of_channel_ids.append(channel_id)

    r.rpush(YT_CHANNELS_QUEUE, *list_of_channel_ids)
    

async def create_single_streamer(name="splattercatgaming"):
    url = base_url+'api/get_streamer'
    data = {'name': name}
    headers = {'Content-Type': 'application/json'}
    exists = False 
    channel_id = yt.get_channel_id_by_name(name)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, json=data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                exists = result["exists"]
            else:
                pass
                #print(f"Error: {response.status}")   
    if not exists:
        url = base_url+"create_streamer/"
        data = {
                "name": name,
                "email": "",
                "twitter": "",
                "twitter_followers": 0,
                "instagram": "",
                "instagram_followers": 0,
                "twitch_url": "wanderbot",
                "twitch_subs": 0,
                "youtube_url": None,
                "youtube_subs": 0,
                "country": "","genres":[]
                }
        stats = yt.channel_statistics(channel_id)
        data["youtube_subs"] = int(stats[channel_id]["youtube_subscribers"])
        data["youtube_url"] = channel_id
        description = stats[channel_id]["description"]
        email = yt.emailFinder(description)
        if email:
            data["email"]=email[0]
        
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

        pprint(data)


        


loop = asyncio.get_event_loop()
loop.run_until_complete(worker_get_all_games_by_splatter_cat())
#loop.run_until_complete(create_single_streamer())
