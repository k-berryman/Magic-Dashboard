"""Models for app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column(db.String(50),
        nullable=False)

    email = db.Column(db.String(50),
        nullable=False,
        unique=True)

    username = db.Column(db.String(25),
        nullable=False,
        unique=True)

    password = db.Column(db.String(500),
        nullable=False)




class Card(db.Model):
    """Card."""

    __tablename__ = "cards"

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column(db.String(150),
        nullable=False)

    picture = db.Column(db.String(500),
        nullable=False)

    cmc = db.Column(db.String(500),
        nullable=False)

    price = db.Column(db.Float,
        nullable=False)

    colors = db.Column(db.String(20),
        nullable=False)


class Deck(db.Model):
    """Deck."""

    __tablename__ = "decks"

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column(db.String(150),
        nullable=False)
