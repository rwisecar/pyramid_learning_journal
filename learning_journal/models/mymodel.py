import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    Unicode,
)

from .meta import Base


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    # creation_date = Column(DateTime, default=datetime.date)
    body = Column(Unicode)


Index('my_index', Entry.title, unique=True, mysql_length=255)
