from sqlalchemy import MetaData, Column, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    playlist = Column(String)
    timezone = Column(String)
    token = Column(PickleType)
    
    def __init__(self, description):
        self.description = description


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(metadata=metadata)        