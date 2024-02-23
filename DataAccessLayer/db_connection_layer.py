from datetime import datetime
from sqlalchemy import delete, insert, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import joinedload, query
from .models import Streamer, Video, Genre, Genre_Streamer_Association
from sqlalchemy.future import select
from typing import Dict, List, Any
from contextlib import asynccontextmanager
import datetime
from dotenv import load_dotenv
import os


load_dotenv()
neondb = os.getenv("NEONDB_TOKEN")

DATABASE_URL = f"postgresql+asyncpg://{neondb}"
engine = create_async_engine(url=DATABASE_URL, 
                             echo=True, 
                             future=True, 
                            query_cache_size=0)

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
        end_r = []
        for row in result.unique():
            end_r.append(streamer_to_dict(row[0].__dict__))
        return {"streamers": end_r}

    async def api_get_all_streamers_paginated(self, page_number=1, items_per_page = 5):
        offset = (page_number-1) * items_per_page
        query = text(f"SELECT * FROM streamers LIMIT {items_per_page} OFFSET {offset}")
        result = await self.db_session.execute(query)
        end_r = {"streamers":[]}
        for row in result.unique():
            end_r["streamers"].append(list(row))
        return end_r

    async def get_all_streamers_paginated(self, page_number=1, items_per_page = 50):
        offset = (page_number-1) * items_per_page
        query =  (select(Streamer)
                    .join(Genre_Streamer_Association)
                    .join(Genre)
                    .offset(offset)
                    .limit(items_per_page))


        result = await self.db_session.execute(query)
        end_r = {"streamers":[]}
        for row in result.unique():
            end_r["streamers"].append(list(row))
        return end_r



    async def filter_streamers_by_genre(self, filters: Dict[str, list]):
        query = create_filter_query(filters)
        result = await self.db_session.execute(query)
        #result = result.unique()
        end_r = {"streamers":[]}
        #for chunk in result.partitions():
        #  for row in chunk:
        #        end_r["streamers"].append(streamer_to_dict(row[0].__dict__))
        for row in result.unique():
           end_r["streamers"].append(list(row))

        return end_r

    async def add_video_history_streamer(self, id: int, data: List[Dict[Any, Any]]):
        streamer_owner: Streamer | None = await self.db_session.get(Streamer, id)
        if not streamer_owner:
            return
        await self.db_session.execute(delete(Video).where(Video.owner == id))
        tmp = []
        for v in data:
            v["owner"] = id
            v["upload_date"] = datetime.datetime.strptime(
                v["upload_date"], "%Y-%m-%d"
            ).date()
            tmp.append(v)
        await self.db_session.execute(insert(Video).values(tmp))
        await self.db_session.commit()
        # await self.db_session.commit()

    async def api_get_streamer(self, data: Dict[str, Any]):
        rows = []
        if "id" in data:
            rows = await self.db_session.get(Streamer, data["id"])
            if rows == None:
                return False
            return True

        elif "channel_id" in data:
            query = select(Streamer).where(Streamer.youtube_url == data["channel_id"])
        else:
            query = select(Streamer).where(Streamer.name == data["name"])

        rows = await self.db_session.execute(query)
        rows = rows.unique().first()
        if rows == None:
            return False
        return True


def streamer_to_dict(s: Dict[str, Any]):
    dict = {
        "id": s["id"],
        "name": s["name"],
        "email": s["email"],
        "twitter": s["twitter"],
        "twitter_followers": s["twitter_followers"],
        "instagram": s["instagram"],
        "instagram_followers": s["instagram_followers"],
        "twitch_url": s["twitch_url"],
        "twitch_subs": s["twitch_subs"],
        "youtube_url": s["youtube_url"],
        "youtube_subs": s["youtube_subs"],
        "country": s["country"],
        # Assuming Video also has a to_dict method
        # "videos": [video.to_dict() for video in s.videos],
    }
    return dict


def create_filter_query(filters: Dict[str, Any]):
    query = (
        select(Streamer)
        .join(Genre_Streamer_Association)
        .join(Genre)
        .offset(0)
        .limit(10)
        .where(Genre.name.in_(filters["genres"]))) #.options(joinedload(Streamer.videos))
    if "youtube" in filters["platforms"]:
        query = query.filter(Streamer.youtube_url.isnot(None))
    if "twitch" in filters["platforms"]:
        query = query.filter(Streamer.twitch_url.isnot(None))
    return query


@asynccontextmanager
async def local_data_access():
    async with async_session() as session:
        async with session.begin():
            yield StreamerDAL(session)
