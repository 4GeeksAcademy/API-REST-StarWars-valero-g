import datetime
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, Table, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(String(60), nullable = False)
    lastname: Mapped[str] = mapped_column(String(60), nullable = False)
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable = False) # type: ignore
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    favourites_planet: Mapped[List["Planets"]] = relationship(secondary="favoritos", back_populates="users")
    favourites_character: Mapped[List["Characters"]] = relationship(secondary="favoritos", back_populates="users")

    def serialize(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "created_date" : self.created_date,
            "email": self.email
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__= "planet"

    id: Mapped[int]  = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(60), nullable = False)
    size: Mapped[int] = mapped_column(nullable = False)
    gravity: Mapped[bool] = mapped_column(Boolean())
    users: Mapped[List["User"]] = relationship(secondary="favoritos", back_populates="favourites_planet")

    def serialize(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "size": self.size,
            "gravity": self.gravity
        }

class Characters(db.Model):
    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(60), nullable = False)
    age: Mapped[int] = mapped_column(nullable = False)
    users: Mapped[List["User"]] = relationship(secondary="favoritos", back_populates="favourites_character")

    def serialize(self):
        return{
            "id" : self.id,
            "name": self.name,
            "age": self.age
        }



favoritos = Table(
    "favoritos",
    db.metadata,
    Column("id", Integer, primary_key = True, autoincrement=True),
    Column("user_id", ForeignKey("user.id"),  nullable = False),
    Column("planet_id", ForeignKey("planet.id"),  nullable = True),
    Column("character_id", ForeignKey("character.id"),  nullable = True)
    )