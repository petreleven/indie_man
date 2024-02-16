import requests
import pprint
from dotenv import load_dotenv
import os

load_dotenv()
rawg_api_key = os.getenv("RAWG_TOKEN")
# url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indiegame'
# url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=20&tags=2d,Platformer,singleplayer,multiplayer&ordering=rating'
# url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=4&search=Solium%20Infernum'


def rawg_genre_endpoint(game: str):
    game_names = game.split("_")
    game = "%20".join(game_names)
    url = f"https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=1&search={game}"
    data = url_req(url)
    return data


def url_req(url):
    res = requests.get(url)
    set_of_genre = set()

    if res.status_code == 200:
        res = res.json()
        data = res["results"]
        # pprint.pprint(data)
        for x in data:
            genres = x["genres"]
            for item in genres:
                name_of_genre = item["name"].lower()
                slug_of_genre = item["slug"].lower()
                set_of_genre.add(name_of_genre)
                set_of_genre.add(slug_of_genre)
        return set_of_genre
    return None
