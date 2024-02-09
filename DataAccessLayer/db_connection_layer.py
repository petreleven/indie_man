from sqlalchemy.ext.asyncio import( 
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession)
from .models import (
    Streamer, 
    Video, 
    Genre, 
    Genre_Streamer_Association)
from sqlalchemy.future import select
from typing import( 
    Dict, 
    List)
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
print(os.path.abspath)
load_dotenv()
neondb = os.getenv("NEONDB_TOKEN")




DATABASE_URL = f"postgresql+asyncpg://{neondb}"
engine = create_async_engine(url=DATABASE_URL, echo=True, future=True)
# sessionmaker version
async_session = async_sessionmaker(engine, expire_on_commit=False)


class StreamerDAL:
    def __init__(self, session: AsyncSession):
        self.aa = "a"
        self.db_session = session

    async def create_stremer(self, streamer_dict: dict):
        new_streamer = Streamer(
            name=streamer_dict["name"],
            email=streamer_dict["email"],
            twitter=streamer_dict["twitter"],
            twitter_followers=streamer_dict["twitter_followers"],
            instagram=streamer_dict["instagram"],
            instagram_followers=streamer_dict["instagram_followers"],
            twitch_url=streamer_dict["twitch_url"],
            twitch_subs=streamer_dict["twitch_subs"],
            youtube_url=streamer_dict["youtube_url"],
            youtube_subs=streamer_dict["youtube_subs"],
            country=streamer_dict["country"],
        )
        has_genres_associated = "genres" in streamer_dict
        _genres: List[Genre] = []
        if has_genres_associated:
            for g in streamer_dict["genres"]:
                _genres.append(Genre(name=g))
        if _genres:
            new_streamer.genres = _genres

        try:
            self.db_session.add(new_streamer)
        except Exception as e:
            await self.db_session.rollback()
        finally:
            await self.db_session.flush()

    async def get_all_streamers(self):
        result = await self.db_session.execute(select(Streamer).order_by(Streamer.id))
        return {"streamers": [streamer.to_dict() for streamer in result]}

    async def filter_streamers_by_genre(self, filters: Dict[str, list]):
        query = (
            select(Streamer)
            .join(Genre_Streamer_Association)
            .join(Genre)
            .where(Genre.name.in_(filters["genres"]))
        )
        result = await self.db_session.execute(query)
        end_r = []
        for chunk in result.partitions():
            for row in chunk:
                print(row[0].__dict__)
                end_r.append(row[0].name)
        print(end_r)

        data = {"streamers": [s.to_dict() for s in result.fetchall()]}
        return "finished db"


@asynccontextmanager
async def local_data_access():
    async with async_session() as session:
        async with session.begin():
            yield StreamerDAL(session)
