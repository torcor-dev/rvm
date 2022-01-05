from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.schema import MetaData, Table
import yaml
from pathlib import Path
from sqlalchemy import create_engine, text, select, func


from db.models import Media, RedditMeta, Subreddit, Tag
from db.query_builder import QueryBuilder

class Db:
    def __init__(self) -> None:
        self.engine = self._create_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _create_engine(self):
        path = str(Path.home()) + "/.secrets/database.yaml"
        with open (path, "r") as f:
            secrets = yaml.load(f, Loader=yaml.Loader)

        return create_engine(secrets["sql-alch"])

    def execute(self, stmt):
        with self.engine.connect() as conn:
            res = conn.execute(stmt)
        return res

    def tag_subbreddit(self, subreddit, *tags):
        errors = []
        sub = self.session.query(Subreddit).filter_by(name=subreddit).first()
        for t in tags:
            try:
                tag = self.create_tag_if_not_exists(t)
                sub.tags.append(tag)
            except:
                errors.append(t)
            else:
                self.session.commit()

        return errors

    def remove_subreddit_tag(self, subreddit, tag):
        sub = self.session.query(Subreddit).filter_by(name=subreddit).first()
        for t in sub.tags:
            if t.name == tag:
                sub.tags.remove(t)
        self.session.commit()


    def create_tag_if_not_exists(self, tag_name):
        tag = self.session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(tag_name)
            self.session.add(tag)
            self.session.commit()
        return tag
                

