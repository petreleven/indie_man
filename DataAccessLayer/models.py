from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Date

Base = declarative_base()


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
    twitch_url = Column(String)
    twitch_subs = Column(Integer)
    youtube_url = Column(String)
    youtube_subs = Column(Integer)
    # country
    country = Column(String)
    genres = relationship(
        "Genre",
        secondary="genre_streamer_associations",
        back_populates="streamers",
        lazy="selectin",
    )
    videos = relationship("Video", back_populates="streamer")

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "twitter": self.twitter,
            "twitter_followers": self.twitter_followers,
            "instagram": self.instagram,
            "instagram_followers": self.instagram_followers,
            "twitch_url": self.twitch_url,
            "twitch_subs": self.twitch_subs,
            "youtube_url": self.youtube_url,
            "youtube_subs": self.youtube_subs,
            "country": self.country,
            # Assuming Video also has a to_dict method
            "videos": [video.to_dict() for video in self.videos],
        }


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("streamers.id"))
    views = Column(Integer)
    comments = Column(Integer)
    upload_date = Column(Date)
    likes = Column(Integer)
    streamer = relationship("Streamer", back_populates="videos", lazy="selectin")


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
