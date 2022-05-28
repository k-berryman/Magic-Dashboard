"""test Flask with this"""

from flask import Flask, render_template, jsonify, redirect, flash, session, request, Markup
from forms import AddCardForm, RegisterForm, LoginForm, DeckForm
from models import connect_db, db, User, Card, Deck
import requests
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'TESTINGGG'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///magicDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


@app.route('/')
def home():
    return redirect("/login")


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
        return redirect(f'/dashboard/{username}')

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if "sessionUsername" in session:
        sessionUsername = session['sessionUsername']
        return redirect(f'/dashboard/{sessionUsername}')

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

            return redirect(f'/dashboard/{username}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    session.clear()
    #session.pop('sessionUsername')
    flash('Goodbye! Logging out now..')
    return redirect('/login')


@app.route('/dashboard/<string:username>', methods=["GET", "POST"])
def dashboard(username):

    if "sessionUsername" not in session:
        flash('Please login first!')
        return redirect('/')

    form = AddCardForm()
    user = User.query.filter_by(username=username).first()

    # if it's a request with a valid CSRF Token
    if form.validate_on_submit():
        # retrieve data from form
        cardName = form.cardName.data

    try:
        if request.method == 'POST':
            resp = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={cardName}")
            data = resp.json()
            pic = data["image_uris"]["normal"]

            # add new user's username to session
            session['sessionCard'] = cardName

        else:
            pic = "https://preview.redd.it/qnnotlcehu731.jpg?auto=webp&s=55d9e57e829608fc8e632eb2e4165d816288177c"


        # Get Deck data
        deckCards = Card.query.all();

        return render_template("dashboard.html", form=form, user=user, pic=pic, deckCards=deckCards)
    except:
        return redirect('/error404')


@app.route('/rand', methods=["GET", "POST"])
def rand():
    resp = requests.get("https://api.scryfall.com/cards/random")

    data = resp.json()
    pic = data["image_uris"]["normal"]
    #print()

    # using the APIs JSON data, return that to browser
    #return jsonify(data)
    return render_template("rand.html", pic=pic)


@app.route('/error404')
def error404():
    return render_template("404.html")


@app.route('/addingcard/<string:username>', methods=["GET", "POST"])
def addCard(username):
    if "sessionUsername" not in session:
        flash('Please login first!')
        return redirect('/')

    if "sessionCard" not in session:
        flash('Please search for a card!')
        return redirect('/')

    user = User.query.filter_by(username=username).first()

    cardName = session['sessionCard']

    try:
        resp = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={cardName}")
        data = resp.json()

        # Get Card Data
        name = data["name"]
        picture = data["image_uris"]["normal"]
        cmc = data["cmc"]
        price = data["prices"]["usd"]
        type = data["type_line"]

        # Send to DB
        newCard = Card(name=name, picture=picture, cmc=cmc, price=price, type=type, deck_id=1)
        db.session.add(newCard)
        db.session.commit()

        return redirect(f'/dashboard/{username}')
        #return render_template("temp.html", user=user, card=cardName, name=name, picture=picture, cmc=cmc, price=price, colors=colors)

    except:
        return redirect('/error404')


@app.route('/removingcard/<string:username>', methods=["GET", "POST"])
def removeCard(username):
    if "sessionUsername" not in session:
        flash('Please login first!')
        return redirect('/')

    user = User.query.filter_by(username=username).first()

    try:
        resp = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={cardName}")
        data = resp.json()

        # Get Card Data
        name = data["name"]
        picture = data["image_uris"]["normal"]
        cmc = data["cmc"]
        price = data["prices"]["usd"]
        type = data["type_line"]

        # Send to DB


        return redirect(f'/dashboard/{username}')
        #return render_template("temp.html", user=user, card=cardName, name=name, picture=picture, cmc=cmc, price=price, colors=colors)

    except:
        return redirect('/error404')


@app.route('/addDeck', methods=["GET", "POST"])
def addDeck():
    form = DeckForm()
    if request.method == 'POST':
        # if it's a request with a valid CSRF Token
        if form.validate_on_submit():
            # retrieve data from form
            commander = form.commander.data
        return redirect("/")

    else:
        return render_template("addDeck.html", form=form)


@app.route('/expenseChart', methods=["GET", "POST"])
def expenseChart():
    return render_template('expenseChart.html')

@app.route('/manaCurveChart', methods=["GET", "POST"])
def manaCurveChart():
    return render_template('manaCurveChart.html')
