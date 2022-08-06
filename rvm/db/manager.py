import datetime
import yaml

from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import sessionmaker
from pathlib import Path
from sqlalchemy import create_engine, func


from rvm.db.models import Media, RedditMeta, Subreddit, Tag
from rvm.db.query_builder import QueryBuilder

class Manager:
    def __init__(self) -> None:
        self._root_path = ""
        self.db = Db()

    @property
    def root_path(self):
        return self._root_path
    
    @root_path.setter
    def root_path(self, path):
        self._root_path = path.strip().rstrip('/') + '/'

    def new_query(self):
        self.query = QueryBuilder(self.db.session)
        self.query.add_model(Media)
        #self.query.distinct = Media.id
        self.query.group_by(Media.id)
        #self.query.add_model(RedditMeta)
        self.query.add_join(RedditMeta.media)
        self.query.add_join(Subreddit)
        self.query.add_join(Subreddit.tags)

    def add_query_filter(self, filter, condition):
        if filter == Filters.TITLE:
            self.query.add_filter((RedditMeta.title.ilike(f'%{condition}%')))
        if filter == Filters.ASPECT_RATIO:
            self.query.add_filter((condition(Media.aspect_ratio)))
        if filter == Filters.RESOLUTION:
            self.query.add_filter(condition(Media.width,Media.height))
        if filter == Filters.AGE:
            day = datetime.datetime.now() - datetime.timedelta(days=condition)
            self.query.add_filter(RedditMeta.created >= day.timestamp())
            self.query.distinct = None
            self.query.order_by(func.max_(RedditMeta.created), True)
        if filter == Filters.SCORE:
            self.query.add_filter(RedditMeta.score > condition)
        if filter == Filters.FORMATS:
            self.query.add_filter(func.lower(Media.format).in_(condition))
        if filter == Filters.TAGS_INCLUDE:
            self.query.add_filter(func.lower(Tag.name).in_(condition))
        if filter == Filters.TAGS_EXCLUDE:
            self._exclude_tags(condition)
        if filter == Filters.SUBREDDITS_INCLUDE:
            self.query.add_filter(func.lower(Subreddit.name).in_(condition))
        if filter == Filters.SUBREDDITS_EXCLUDE:
            self._exclude_subs(condition)

    def _exclude_subs(self, condition):
        alias_sub = aliased(Subreddit)
        subquery = self.db.session.query(alias_sub.name)\
                .filter(func.lower(alias_sub.name).in_(condition))\
                .filter(alias_sub.name==Subreddit.name)\
                .exists()
        self.query.add_filter(~subquery)

    def _exclude_tags(self, condition):
        alias_sub = aliased(Subreddit)
        subquery = self.db.session.query(alias_sub.name)\
                .join(alias_sub.tags)\
                .filter(func.lower(Tag.name).in_(condition))\
                .filter(alias_sub.name==Subreddit.name)\
                .exists()
        #self._add_tag_model(self.query)
        self.query.add_filter(~subquery)

    def debug_query(self, limit=-1):
        #if len(self.query.models) == 2:
        #    for media, meta in self.query.build()[:limit]:
        #        print(media.height, 'x', media.width)
        #else:
        #    for row in self.query.build()[:limit]:
        #        print(row.RedditMeta.full_permalink())
        #        print(row.Tag if hasattr(row, 'Tag') else None)
        #        print(row.Subreddit if hasattr(row, 'Subreddit') else None)

        print('Total rows:', self.query.build().count())
        print(str(self.query.build()))

    def list_files(self):
        result = []
        for media in self.query.build():
            result.append(self.root_path + media.get_file_path())

        return result


class TagManager:
    def __init__(self) -> None:
        self.db = Db()

    def tag_subs(self, subs, tags):
        result = []
        for sub in subs:
            sub = self.db.session.query(Subreddit).filter(func.lower(Subreddit.name)==sub).first()
            if not sub:
                result.append(f'Error: Subreddit "{sub}" does not exist')
            else:
                for tag in tags:
                    result.append(self.tag_sub(sub, tag))
        return '\n'.join(result)
    
    def tag_sub(self, sub, tag):
        tag = self._create_tag_if_not_exists(tag)
        if tag in sub.tags:
            return f'Warning: {sub} was already tagged with {tag}'
        else:
            sub.tags.append(tag)
            self.db.session.commit()
            return f'Success: {sub} tagged with {tag}'

    def untag_subs(self, subs, tags):
        result = []
        for sub in subs:
            sub = self.db.session.query(Subreddit).filter(func.lower(Subreddit.name)==sub).first()
            if not sub:
                result.append(f'Error: Subreddit "{sub}" does not exist')
            else:
                for tag in tags:
                    result.append(self.untag_sub(sub, tag))
        return '\n'.join(result)

    def untag_sub(self, sub, tag):
        for t in sub.tags:
            if t.name == tag:
                sub.tags.remove(t)
                self.db.session.commit()
                return f'Success: {tag} was removed from {sub}'

        return f'Warning: Tag {tag} was not found in {sub}'

    def list_tags(self):
        return [tag.name for tag in self.db.session.query(Tag)]

    def untagged_subs(self):
        #alias_tags = aliased(Subreddit.tags)
        #subquery = self.db.session.query(alias_tags)\
        #        .group_by(alias_tags.subreddit_name)
        subquery = self.db.session.query(Subreddit.name)\
                .join(Subreddit.tags)\
                .group_by(Subreddit.name)
        query = self.db.session.query(Subreddit.name)\
                .filter(Subreddit.name.not_in(subquery))

        return [sub.name for sub in query]

    def list_sub_tags(self, sub):
        query = self.db.session.query(Tag)\
                .join(Subreddit.tags)\
                .filter(func.lower(Subreddit.name)==sub)
        return [tag.name for tag in query]

    def tagged_subs(self, tag):
        query = self.db.session.query(Subreddit)\
                .join(Subreddit.tags)\
                .filter(func.lower(Tag.name)==tag)\
                .order_by(Subreddit.name)
        return [sub.name for sub in query]


    def _create_tag_if_not_exists(self, tag_name):
        tag = self.db.session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(tag_name)
            self.db.session.add(tag)
            self.db.session.commit()
        return tag
        

class Db:
    def __init__(self) -> None:
        self.engine = self._create_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _create_engine(self):
        path = str(Path.home()) + '/.secrets/database.yaml'
        with open (path, 'r') as f:
            secrets = yaml.load(f, Loader=yaml.Loader)

        return create_engine(secrets['sql-alch'])


    def execute(self, stmt):
        with self.engine.connect() as conn:
            res = conn.execute(stmt)
        return res


class Filters:
    TITLE = 'TITLE'
    ASPECT_RATIO = 'ASPECT_RATIO'
    AGE = 'AGE'
    SCORE = 'SCORE'
    TAGS_INCLUDE = 'TAGS_INCLUDE'
    TAGS_EXCLUDE = 'TAGS_EXCLUDE'
    SUBREDDITS_INCLUDE = 'SUBREDDITS_INCLUDE'
    SUBREDDITS_EXCLUDE = 'SUBREDDITS_EXCLUDE'
    RESOLUTION = 'RESOLUTION'
    NO_STRIPS = 'NO_STRIPS'
    FORMATS = 'FORMATS'

    LANDSCAPE = lambda x: x > 1.2
    PORTRAIT = lambda x: x < 0.8
    APPROX_RATIO = lambda x, y: lambda z: func.abs(z - x) <= y
    NO_COMIC_STRIPS = lambda x: x > 0.4
    HIGH_RES = lambda x, y: x * y > 1600 * 1200
    ABSURD_RES = lambda x, y: x * y > 3200 * 2400 
    ALL_FORMATS = 'all'
    VIDEOS = ['gif', 'mp4']
    IMAGES = ['jpg', 'png']


