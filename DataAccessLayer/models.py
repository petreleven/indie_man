from sqlalchemy.orm import   DeclarativeBase, relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.ext.asyncio import AsyncAttrs
class Base(DeclarativeBase, AsyncAttrs):
    pass


class Genre_Streamer_Association(Base):
    __tablename__ = "genre_streamer_associations"
    id = Column(Integer, primary_key=True)
    streamer_id = Column(Integer, ForeignKey("streamers.id"))
    genre_id = Column(Integer, ForeignKey("genres.id"))


class Streamer(Base):
    __tablename__ = "streamers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    # socials
    twitter = Column(String)
    twitter_followers = Column(Integer)
    instagram = Column(String)
    instagram_followers = Column(Integer)
    # channels
    twitch_url = Column(String, nullable=True)
    twitch_subs = Column(Integer)
    youtube_url = Column(String, nullable=True)
    youtube_subs = Column(Integer)
    # country
    country = Column(String)
    genres = relationship(
        "Genre",
        secondary="genre_streamer_associations",
        back_populates="streamers",
        lazy="joined",
    )
    videos = relationship("Video", back_populates="streamer")



class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("streamers.id"))
    views = Column(Integer)
    comments = Column(Integer)
    upload_date = Column(Date)
    likes = Column(Integer)
    streamer = relationship(
        "Streamer", back_populates="videos"    )


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    streamers = relationship(
        "Streamer",
        secondary="genre_streamer_associations",
        back_populates="genres",
        lazy="selectin",
    )
