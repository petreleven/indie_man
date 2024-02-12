import requests
import pprint

rawg_api_key = ""


class GalacticGenresRawg:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_genre(game_title: str):
        # game_title should be single word if whitespace in title use + for spaces eg (Solium+Infernum)
        game_title_copy = game_title.lower().strip()
        print(game_title_copy)
        game_title = game_title.split(" ")
        game_title = "+".join(game_title).capitalize()
        url = f"https://api.rawg.io/api/games?key={rawg_api_key}&genre=indie&page_size=4&search={game_title}"
        res = requests.get(url)
        if res.status_code == 200:
            res = res.json()
            data = res["results"]
            # pprint.pprint(data)
            game_names = {}
            for x in data:
                genres = x["genres"]
                set_of_genre = set()
                for item in genres:
                    name_of_genre = item["name"].lower()
                    slug_of_genre = item["slug"].lower()
                    print(name_of_genre)
                    set_of_genre.add(name_of_genre)
                    set_of_genre.add(slug_of_genre)
                game_names[x["name"].lower()] = set_of_genre.copy()
                set_of_genre.clear()

            pprint.pprint(game_names)
            if (game_title_copy in game_names.keys()) and len(
                game_names[game_title_copy]
            ) > 0:
                return game_names[game_title_copy]
            return False
        else:
            return False


result = GalacticGenresRawg.get_genre("pioneers of pagonia")
print("RESULTS")
print(result)
