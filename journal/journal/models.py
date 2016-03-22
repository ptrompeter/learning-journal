import datetime 

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,
    UnicodeText,
    DateTime,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    )

class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')]

    def __init__(self,request):
        pass

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=128), unique=True, nullable=False)
    text = Column(UnicodeText)
    created = Column(DateTime(), default=datetime.datetime.utcnow())

    @property
    def markeddown(self):
        return render_markdown(self.text) 
    

#Index('journal_index', Entry.title, unique=True)
