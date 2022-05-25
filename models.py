from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


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


    @classmethod
    def register(cls, name, email, username, password):
        """Register user w/ hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)

        # turn bytestring into normal unicode utf8 string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/ username and hashed password
        return cls(name=name, email=email, username=username, password=hashed_utf8)


    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists and password is correct. Return user if valid; else, return False """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False



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

    user_id = db.Column(db.Integer,
        db.ForeignKey('users.id'))

    card_id = db.Column(db.Integer,
        db.ForeignKey('cards.id'))
