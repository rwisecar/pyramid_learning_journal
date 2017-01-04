import datetime

from sqlalchemy import (
    Column,
    Date,
    Index,
    Integer,
    Unicode,
)

from .meta import Base


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    creation_date = Column(Date)
    body = Column(Unicode)

    def to_json(self):
        """Return string representation of database entries."""
        return {
            "id": self.id,
            "title": self.title,
            "creation_date": self.creation_date.strftime("%M %d, %Y"),
            "body": self.body,
        }
