import requests
import pprint
from dotenv import load_dotenv
import os

load_dotenv()
rawg_api_key = os.getenv("RAWG_TOKEN")
#url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indiegame'
#url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=20&tags=2d,Platformer,singleplayer,multiplayer&ordering=rating'
#url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=4&search=Solium%20Infernum'
url = f'https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=4&search=fabledom%20Solium%20Infernum'
res = requests.get(url)
if res.status_code == 200:
    res = res.json()
    data = res['results']
    #pprint.pprint(data)
    game_names = {}
    for x in data:
        genres =x['genres']
        set_of_genre = set()
        for item in genres:
            name_of_genre = item['name'].lower()
            slug_of_genre = item['slug'].lower()
            print(name_of_genre)
            set_of_genre.add(name_of_genre)
            set_of_genre.add(slug_of_genre)
        game_names[x['name']] = set_of_genre.copy()
        set_of_genre.clear()

    pprint.pprint(game_names)
else:
    pprint.pprint(res)
