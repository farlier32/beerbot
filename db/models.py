from sqlalchemy import Column, Integer, String, Float
from db.database import Base


class Beer(Base):
    __tablename__ = "beers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brewery = Column(String)
    style = Column(String)
    alcohol = Column(Float)
    release_date = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    ibu = Column(Integer, nullable=True)
    hops = Column(String, nullable=True)
    malt = Column(String, nullable=True)
    additives = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nick = Column(String, index=True)
    name = Column(String)
    last_name = Column(String, nullable=True)
    permissions = Column(Integer)