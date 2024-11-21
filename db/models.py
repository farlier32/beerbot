from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, SmallInteger
from db.database import Base
from sqlalchemy.orm import relationship

class Beer(Base):
    __tablename__ = "beers"
    beer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1000), nullable=False)
    brewery = Column(String(1000))
    style = Column(String(255))
    alcohol = Column(Float)
    release_date = Column(Date)
    rating = Column(Float)
    ibu = Column(Integer)
    hops = Column(String(255))
    malts = Column(String(255))
    additives = Column(String(255))

    # Связь с Place через place_beers
    places = relationship("PlaceBeer", back_populates="beer")

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)  # Идентификатор пользователя
    nickname = Column(String(255))  # Никнейм пользователя
    first_name = Column(String(255))  # Имя пользователя
    last_name = Column(String(255))  # Фамилия пользователя
    permissions = Column(SmallInteger)  # Права пользователя

class Rating(Base):
    __tablename__ = 'ratings'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)  # Внешний ключ на пользователя
    beer_id = Column(Integer, ForeignKey('beers.beer_id'), primary_key=True)  # Внешний ключ на пиво
    rating = Column(SmallInteger)  # Рейтинг



class PlaceBeer(Base):
    __tablename__ = "place_beers"
    place_id = Column(Integer, ForeignKey("places.place_id"), primary_key=True)
    beer_id = Column(Integer, ForeignKey("beers.beer_id"), primary_key=True)

    # Связи с Beer и Place
    beer = relationship("Beer", back_populates="places")
    place = relationship("Place", back_populates="beers_in_place")

class Place(Base):
    __tablename__ = "places"
    place_id = Column(Integer, primary_key=True, index=True)
    place_name = Column(String(255))

    # Связь с Beer через place_beers
    beers_in_place = relationship("PlaceBeer", back_populates="place")