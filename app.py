"""test Flask with this"""

from flask import Flask, render_template, jsonify, redirect, flash, session
from forms import AddForm, RegisterForm, LoginForm
from models import connect_db, db, User, Card
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'TESTINGGG'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///magicDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    # if it's a request with a valid CSRF Token
    if form.validate_on_submit():
        # retrieve data from form
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data

        # add to SQLAlchemy
        newUser = User.register(name, email, username, password)
        db.session.add(newUser)
        db.session.commit()

        # add new user's username to session
        session['sessionUsername'] = newUser.username

        # redirect
        flash('Welcome! Successfully logged in')
        return redirect('/secret')

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    # if it's a request with a valid CSRF Token
    if form.validate_on_submit():
        # retrieve data from form
        username = form.username.data
        password = form.password.data

        # verification
        user = User.authenticate(username, password)

        if user:
            # add user_id to session
            session['sessionUsername'] = user.username

            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template("login.html", form=form)


@app.route('/secret')
def secret():
    if "sessionUsername" not in session:
        flash('Please login first!')
        return redirect('/')

    return "You made it!"



@app.route('/form', methods=["GET", "POST"])
def form():
    form = AddForm()

    # if it's a post request with a valid CSRF Token
    if form.validate_on_submit():
        cardName = form.cardName.data
        return redirect('/answer')

    else:
        return render_template("index.html", form=form)


@app.route('/req')
def req():
    resp = requests.get("https://api.scryfall.com/cards/random")

    data = resp.json()
    pic = data["image_uris"]["normal"]
    #print()

    # using the APIs JSON data, return that to browser
    #return jsonify(data)
    return render_template("card.html", pic=pic)
