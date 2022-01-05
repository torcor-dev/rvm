from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Numeric, UniqueConstraint
from sqlalchemy.sql.schema import ForeignKey, Table

Base = declarative_base()

subreddit_tags = Table("subreddit_tag", Base.metadata,
        Column("tag_name", ForeignKey("tag.name"), primary_key=True),
        Column("subreddit_name", ForeignKey("subreddit.name"), primary_key=True),
    )

media_meta = Table("post_link", Base.metadata,
        Column("media_id", ForeignKey("media.id"), primary_key=True),
        Column("reddit_meta_id", ForeignKey("reddit_meta.id"), primary_key=True),
    )


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    file_name = Column(String, unique=True)
    format = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    aspect_ratio = Column(Numeric)
    size = Column(Numeric)
    media_type = Column(String)

    video = relationship("Video", back_populates="media", uselist=False)
    posts = relationship("RedditMeta", secondary=media_meta, back_populates="media")

    def __repr__(self) -> str:
        return f"Media => id: {self.id}, format: {self.format}, type: {self.media_type}"

    def get_file_path(self) -> str:
        path = f"{self.format}/" +\
            f"{self.file_name[:2]}/" +\
            f"{self.file_name[2:4]}/" +\
            f"{self.file_name[4:6]}/" +\
            f"{self.file_name}.{self.format}"
        return  path

class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    frame_rate = Column(String)
    duration = Column(String)

    media = relationship("Media", back_populates="video")

class Subreddit(Base):
    __tablename__ = "subreddit"

    name = Column(String, primary_key=True)
    tags = relationship("Tag", secondary=subreddit_tags, back_populates="subreddits")
    posts = relationship("RedditMeta")

    def __repr__(self) -> str:
        return f"Subreddit: {self.name}"



class Tag(Base):
    __tablename__ = "tag"

    name = Column(String, primary_key=True)

    subreddits = relationship("Subreddit",
            secondary=subreddit_tags,
            back_populates="tags")
    
    def __init__(self, name: str) -> None:
        self.name = name.lower()

    def __repr__(self) -> str:
        return f"Tag: {self.name}"

class RedditMeta(Base):
    __tablename__ = "reddit_meta"

    id = Column(Integer, primary_key=True)
    author = Column(String)
    created = Column(Integer)
    reddit_id = Column(String, unique=True)
    permalink = Column(String)
    score = Column(Integer)
    subreddit = Column(String, ForeignKey("subreddit.name"))
    title = Column(String)
    url = Column(String)

    media = relationship("Media", secondary=media_meta, back_populates="posts")
