from googleapiclient.discovery import build
from datetime import datetime
from typing import Dict, List, Union
import requests
import re
import bs4
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_TOKEN")


class YoutubeApi:
    def __init__(self) -> None:
        self.youtube = build("youtube", "v3", developerKey=api_key)

    """
    RETURNS CHANNEL ID GIVEN NAME
    """

    def get_channel_id_by_name(self, username: str):
        search_request = self.youtube.search().list(
            q=username, type="channel", part="id", maxResults=1
        )
        # Channel Information
        search_response = search_request.execute()
        channel_id: str = search_response["items"][0]["id"]["channelId"]
        return channel_id

    """THIS SCRAPES ABOUT PAGE
    RETURNS ~TWITTER  ~INSTAGRAM AND TWITCH ACCOUNTS"""

    def scrape_social_media(self, channel_id):
        response = requests.get(
            f"https://www.youtube.com/channel/{channel_id}/about",
            headers={"Accept-Language": "en", "http": "http"},
        )
        if response.status_code == 200:
            html_content = response.text
            html_content = bs4.BeautifulSoup(html_content, "html.parser")

            twitter_pattern = r"[a-zA-Z]witter\.com%2F[a-zA-Z0-9_]+"
            instagram_pattern = r"[a-zA-Z]nstagram\.com%2F[a-zA-Z0-9_]+"
            twitch_pattern = r"[a-zA-Z]witch\.tv%2F[a-zA-Z0-9_]+"

            match_twitter = re.search(
                pattern=twitter_pattern, string=str(html_content)
            )
            match_instagram = re.search(
                pattern=instagram_pattern, string=str(html_content)
            )
            match_twitch = re.search(
                pattern=twitch_pattern, string=str(html_content)
            )
            socials = {"Twitter": None, "Instagram": None, "Twitch": None}

            if match_twitter:
                socials["Twitter"] = match_twitter.group(0)
            if match_instagram:
                socials["Instagram"] = match_instagram.group(0)
            if match_twitch:
                socials["Twitch"] = match_twitch.group(0)
            return socials

        else:
            return response.status_code

    """GIVEN A PLAYLIST ID
    RETURNS CHANNELS IN THE PLAYLIST"""

    def obtain_playlist_of_different_videos(
        self, playlistId="PL6QwxSrxADlmTaU8AMsTGt4BPmsdi659z"
    ):
        playlist = self.youtube.playlistItems().list(
            playlistId=playlistId, part="snippet", maxResults=10  # playlist_id
        )
        playlist_response = playlist.execute()
        # pprint.pprint(playlist_response)

        list_of_recommended_chanels = []
        items = playlist_response["items"]
        for item in items:
            snippet = item["snippet"]
            videoOwnerChannelId = snippet["videoOwnerChannelId"]
            videoOwnerChannelTitle = snippet["videoOwnerChannelTitle"]
            list_of_recommended_chanels.append(videoOwnerChannelTitle)

        print(list_of_recommended_chanels)

    def search_particular_indie_gameplay_channels(
        self, game_name, next_page_token: Union[str, None] = None
    ):
        """
        #gameplay
        #walkthrough
        lets play#
        let's play #
        """
        maxResults = 20
        if next_page_token:
            search = self.youtube.search().list(
                part="snippet",
                q=f"lets play {game_name}",
                maxResults=maxResults,
                pageToken=next_page_token,
            )
        else:
            search = self.youtube.search().list(
                part="snippet",
                q=f"lets play {game_name}",
                maxResults=maxResults,
            )

        search_response = search.execute()

        items = search_response["items"]
        _next_page_token: str = search_response["nextPageToken"]
        dict_of_channel_names: Dict[str, List[dict]] = dict()
        gameplay_keywords = [
            "gameplay",
            "indie",
            "walkthrough",
            "letsplay",
            "let's play",
            "games",
            "game",
            "gaming",
            "playthrough",
            "game commentary",
            "game review",
            "gaming highlights",
            "gaming walkthrough",
            "video game let's play",
            "gamer commentary",
            "game strategies",
            "game tutorials",
            "in-game tips",
            "game streaming",
            "game analysis",
            "gaming guide",
            "gaming adventures",
            "game progress",
            "gaming live stream",
            "game strategies and tactics",
            "video game",
            "game analysis and reviews",
            "game exploration",
        ]

        for item_instance in items:
            snippet = item_instance["snippet"]
            channel_id = snippet["channelId"]
            channel_title = snippet["channelTitle"]
            # Get additional channel information
            channel_info = (
                self.youtube.channels()
                .list(part="snippet", id=channel_id)
                .execute()
            )
            description = channel_info["items"][0]["snippet"][
                "description"
            ].lower()
            # print(description)
            # print("*"*20)
            # Check if the channel description contains gameplay keywords
            if any(keyword in description for keyword in gameplay_keywords):
                dict_of_channel_names[channel_title] = [
                    {"channel_id": channel_id, "description": description}
                ]

        return dict_of_channel_names, _next_page_token

    def video_stats_helper(self, video_ids):
        video_stats_helper_response = (
            self.youtube.videos()
            .list(
                part="statistics",
                id=video_ids,
                fields="items(statistics(viewCount,likeCount,commentCount))",
            )
            .execute()
        )
        return video_stats_helper_response

    def video_stats(self, video):
        videoId = video["id"]["videoId"]
        videoTitle = video["snippet"]["title"]
        publishedAt = self.time_converter(video["snippet"]["publishedAt"])

        return (videoId, publishedAt, videoTitle)

    def time_converter(self, timestamp_str):
        # Parse the timestamp string to a datetime object
        timestamp_utc = datetime.fromisoformat(timestamp_str[:-1])
        # Format the datetime object as a string in a desired format
        formatted_utc_time = timestamp_utc.strftime("%A %H:%M UTC")

        return formatted_utc_time

    def most_popular_or_recent_video(self, channel_id, order: int = 0):
        orderFilter = ["viewCount", "date"]
        channel_response = (
            self.youtube.search()
            .list(
                channelId=channel_id,
                part="snippet",
                order=orderFilter[order],
                fields="items(id,snippet)",
                maxResults=10,
            )
            .execute()
        )
        popular_video = map(
            self.video_stats, [video for video in channel_response["items"]]
        )
        popular_video_copy = [x for x in popular_video]
        stats_response = self.video_stats_helper(
            ",".join([x[0] for x in popular_video_copy])
        )["items"]
        results = []
        for index, video in enumerate(popular_video_copy):
            results.append(
                [video[0], video[1], video[2], stats_response[index]]
            )
        return results

    def get_channel_topics(self, channel_id):
        # Get the uploads playlist of the channel
        channel_request = (
            self.youtube.channels()
            .list(
                id=channel_id,
                part="contentDetails",
            )
            .execute()
        )

        uploads_playlist_id = channel_request["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]

        # Fetch the videos from the uploads playlist
        videos_request = (
            self.youtube.playlistItems()
            .list(
                playlistId=uploads_playlist_id,
                part="snippet",
                maxResults=50,  # You can adjust this value as needed
            )
            .execute()
        )

        # Extract and print the topics from video titles and descriptions
        topics = set()  # Use a set to avoid duplicates
        for video in videos_request["items"]:
            video_title = video["snippet"]["title"]
            video_description = video["snippet"]["description"]

            # You can add more text processing here to extract topics from titles and descriptions
            # For simplicity, let's just use the video titles for now
            topics.add(video_title)

        return topics

    def channel_statistics(self, channelId: str):
        channel_response = (
            self.youtube.channels()
            .list(id=channelId, part="statistics,snippet")
            .execute()
        )
        stats = {}
        for item in channel_response["items"]:
            stats[item["id"]] = {
                "youtube_subscribers": item["statistics"]["subscriberCount"],
                "youtube_video_count": item["statistics"]["videoCount"],
                "youtube_total_views": item["statistics"]["viewCount"],
                "county": (
                    item["snippet"]["country"]
                    if hasattr(item["snippet"], "country")
                    else None
                ),
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            }

        return stats

    # Targets Splattercatgaming video descriptions
    def video_details(self, video_id):  # -> tuple[str | Any, Any]:
        video_response = (
            self.youtube.videos().list(id=video_id, part="snippet").execute()
        )
        description = video_response["items"][0]["snippet"]["description"]
        video_search_tags = video_response["items"][0]["snippet"]["description"]
        pattern = r"https://store\.steampowered\.com/app/(\d+)/(\w+)"
        match = re.search(pattern=pattern, string=description)
        game_played = ""
        if match:
            # steam_link = match.group(0)
            # app_id = match.group(1)
            game_played = match.group(2)
        # print(video_tags)

        return (game_played, video_search_tags)

    @staticmethod
    def emailFinder(data: str):
        patterns = [r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"]
        for p in patterns:
            match = re.findall(pattern=p, string=data)
            if match:
                return match
        return None

    @staticmethod
    def socialsFinder(data: str):
        socials = {"Twitter": None, "Instagram": None, "Twitch": None}
        twitch_pattern = "(^http(s)?://)?((www|en-es|en-gb|secure|beta|ro|www-origin|en-ca|fr-ca|lt|zh-tw|he|id|ca|mk|lv|ma|tl|hi|ar|bg|vi|th)\.)?twitch.tv/(?!directory|p|user/legal|admin|login|signup|jobs)(?P<channel>\w+)"
        twitter_pattern = (
            "https?://twitter.com/[A-Za-z0-9_]+|twitter.com/[A-Za-z0-9_]+"
        )
        instagram_pattern = (
            "https?://instagram.com/[A-Za-z0-9_]+|instagram.com/[A-Za-z0-9_]+"
        )

        twitch_match = re.findall(pattern=twitch_pattern, string=data)
        twitter_match = re.findall(pattern=twitter_pattern, string=data)
        instagram_match = re.findall(pattern=instagram_pattern, string=data)

        if twitch_match and len(twitch_match) > 0:
            socials["Twitch"] = twitch_match[0][-1]
        if twitter_match and len(twitter_match) > 0:
            socials["Twitter"] = twitter_match[0]
        if instagram_pattern and len(instagram_match) > 0:
            socials["Instagram"] = instagram_match[0]

        return socials


def youtube_search_worker():
    yt = YoutubeApi()
    search_data, next_page_token = yt.search_particular_indie_gameplay_channels(
        game_name="go mecha ball"
    )
    list_of_channel_ids = []
    for key, val in search_data.items():
        channel_id, description = val[0]["channel_id"], val[0]["description"]
        # TODO SAVE CHANNEL NAME,ID, DESCRIPTION TO DATABASE if not present
        list_of_channel_ids.append(channel_id)
        social_media = yt.socialsFinder(description)
        scraped = yt.scrape_social_media(channel_id)
        print(social_media)
        print(scraped)
        print(key)
        print(yt.emailFinder(description))
        print("*" * 20)

    # stats = yt.channel_statistics(",".join(list_of_channel_ids))
    # TODO UPDATE SAVED CHANNEL USING CHANNEL ID
    """
    {'UCJnTbRcpBWoZEVutjU743yg': {'youtube_subscribers': '15400', 'youtube_video_count': '703', 'youtube_total_views': '4691844', 
    'county': 'AU', 'thumbnail': 'https://yt3.ggpht.com/nc4MSo3n6Fbkzd4rhuRFK3TwIXDammDnH2s3wWPuqkoAWPS9MgFcg5ZqXZjEuMCSNv-oZYVfXis=s88-c-k-c0x00ffffff-no-rj'}}
    """


youtube_search_worker()

"""
TOTAL SUBS COUNT
TOTAL VIEWS COUNT
TOTAL VIDEO COUNT
COMMENTS OVER RECENT HISTORY
LIKES OVER RECENT HISTORY
VIEWS OVER RECENT HISTORY

RECENT VIDEOS CHART
MOST POPULAR VIDEOS CHART

"""
