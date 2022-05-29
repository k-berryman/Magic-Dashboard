"""test Flask with this"""

from flask import Flask, render_template, jsonify, redirect, flash, session, request, Markup
from forms import AddCardForm, RegisterForm, LoginForm, DeckForm
from models import connect_db, db, User, Card, Deck
import requests
import matplotlib.pyplot as plt
import os


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# use secret key in production or default to our dev one
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')

# production or dev DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///magicDB')

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
    flash('Goodbye! Logging out now..')
    return redirect('/login')

@app.route('/dashboard/<string:username>', defaults={'cardToNamePreview': None}, methods=["GET", "POST"])
@app.route('/dashboard/<string:username>/<string:cardToNamePreview>', methods=["GET", "POST"])
def dashboard(username, cardToNamePreview):

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

        elif cardToNamePreview == None:
            pic = "https://preview.redd.it/qnnotlcehu731.jpg?auto=webp&s=55d9e57e829608fc8e632eb2e4165d816288177c"

        else:
            # Get card ID for card picture
            tempCard = Card.query.filter_by(name=cardToNamePreview).first()

            pic = tempCard.picture


        # Get Deck data
        if "sessionDeckName" in session:
            deckName = session['sessionDeckName']

            # Get cardID to look from Card table to Deck table
            commander = Card.query.filter_by(name=deckName).first()

            deckCards = Card.query.filter_by(deck_id = commander.deck_id).all()
            print('---------------------------------------------------')
            print(deckCards)
            print('---------------------------------------------------')

        else:
            deckName = "All Cards"
            deckCards = Card.query.all();


        usersDecks = Deck.query.all();

        # Make recommended cards
        pic1 = requests.get("https://api.scryfall.com/cards/random").json()["image_uris"]["normal"]
        pic2 = requests.get("https://api.scryfall.com/cards/random").json()["image_uris"]["normal"]
        pic3 = requests.get("https://api.scryfall.com/cards/random").json()["image_uris"]["normal"]
        pic4 = requests.get("https://api.scryfall.com/cards/random").json()["image_uris"]["normal"]
        pic5 = requests.get("https://api.scryfall.com/cards/random").json()["image_uris"]["normal"]

        return render_template("dashboard.html", form=form, user=user, pic=pic, deckCards=deckCards,
            usersDecks=usersDecks, deckName=deckName, rec1=pic1, rec2=pic2, rec3=pic3, rec4=pic4, rec5=pic5)
    except:
        return redirect('/error404')


@app.route('/rand', methods=["GET", "POST"])
def rand():
    resp = requests.get("https://api.scryfall.com/cards/random")

    data = resp.json()
    pic = data["image_uris"]["normal"]

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

        # Get cardID to look from Card table to Deck table
        deckName = session['sessionDeckName']
        commander = Card.query.filter_by(name=deckName).first()
        deck_id = commander.deck_id

        # Send to DB
        newCard = Card(name=name, picture=picture, cmc=cmc, price=price, type=type, deck_id=deck_id)
        db.session.add(newCard)
        db.session.commit()

        return redirect(f'/dashboard/{username}')
        #return render_template("temp.html", user=user, card=cardName, name=name, picture=picture, cmc=cmc, price=price, colors=colors)

    except:
        return redirect('/error404')


@app.route('/removingcard/<string:cardName>', methods=["GET", "POST"])
def removeCard(cardName):
    if "sessionUsername" not in session:
        flash('Please login first!')
        return redirect('/')

    try:
        # Send to DB
        Card.query.filter_by(name=cardName).delete()
        db.session.commit()

        return redirect('/')

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

            try:
                # Get user for user ID
                sessionUsername = session['sessionUsername']
                user = User.query.filter_by(username=sessionUsername).first()

                # Create card for commander
                resp = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={commander}")
                data = resp.json()

                # Get commander data
                name = data["name"]
                picture = data["image_uris"]["normal"]
                cmc = data["cmc"]
                price = data["prices"]["usd"]
                type = data["type_line"]


                # Figure out deck id
                numDecks = Deck.query.count()
                newDeckID = numDecks + 1

                # Send commander card to DB
                newCard = Card(name=name, picture=picture, cmc=cmc, price=price, type=type, deck_id=newDeckID)
                db.session.add(newCard)
                db.session.commit()

                # Get card ID for card ID
                card = Card.query.filter_by(name=name).first()

                # Create new deck and send to DB
                newDeck = Deck(name=commander, user_id=user.id, card_id=card.id)
                db.session.add(newDeck)
                db.session.commit()

                # Get deck.name for deckname in sesison
                deck = Deck.query.filter_by(name=name).first()

                session['sessionDeckName'] = deck.name

                return redirect("/")

            except:
                return redirect("/error404")

    return render_template("addDeck.html", form=form)


@app.route('/setDeck/<string:deckname>', methods=["GET", "POST"])
def setDeck(deckname):
    # add deck to session
    session['sessionDeckName'] = deckname

    return redirect(f"/previewOnly/{deckname}")


@app.route('/previewOnly/<string:cardname>', methods=["GET", "POST"])
def previewOnly(cardname):
    # Get card ID for card picture
    card = Card.query.filter_by(name=cardname).first()

    # Get user for username
    sessionUsername = session['sessionUsername']
    user = User.query.filter_by(username=sessionUsername).first()

    return redirect(f'/dashboard/{user.username}/{card.name}')


@app.route('/expenseChart', methods=["GET", "POST"])
def expenseChart():

    cat1Sum = 0   # $0 - $0.49
    cat2Sum = 0   # $0.50 - $0.74
    cat3Sum = 0   # $0.75 - $0.99
    cat4Sum = 0   # $1.00 - $1.99
    cat5Sum = 0   # $2.00 - $4.99
    cat6Sum = 0   # $5.00 +

    # Get deck cards
    deckName = session['sessionDeckName']
    commander = Card.query.filter_by(name=deckName).first()
    deckCards = Card.query.filter_by(deck_id = commander.deck_id).all()

    for card in deckCards:
        print("---- ", card.price, " ---")
        if card.price < .49:
            cat1Sum = cat1Sum + 1

        elif card.price >= .5 and card.price <= .74:
            cat2Sum = cat2Sum + 1

        elif card.price >= .75 and card.price <= 0.99:
            cat3Sum = cat3Sum + 1

        elif card.price >= 1 and card.price <= 1.99:
            cat4Sum = cat4Sum + 1

        elif card.price >= 2 and card.price <= 4.99:
            cat5Sum = cat5Sum + 1

        else:
            cat6Sum = cat6Sum + 1

    data = [cat1Sum, cat2Sum, cat3Sum, cat4Sum, cat5Sum, cat6Sum]

    return render_template('expenseChart.html', data=data)


@app.route('/manaCurveChart', methods=["GET", "POST"])
def manaCurveChart():

    cat1Sum = 0   # 0 cards
    cat2Sum = 0   # 1 card
    cat3Sum = 0   # 2 cards
    cat4Sum = 0   # 3 cards
    cat5Sum = 0   # 4 cards
    cat6Sum = 0   # 5 cards
    cat7Sum = 0   # 6 cards
    cat8Sum = 0   # 7 cards
    cat9Sum = 0   # 8 cards

    # Get deck cards
    deckName = session['sessionDeckName']
    commander = Card.query.filter_by(name=deckName).first()
    deckCards = Card.query.filter_by(deck_id = commander.deck_id).all()

    for card in deckCards:
        print("---- ", card.cmc, " ---")
        if card.cmc == 0:
            cat1Sum = cat1Sum + 1

        elif card.cmc == 1:
            cat2Sum = cat2Sum + 1

        elif card.cmc == 2:
            cat3Sum = cat3Sum + 1

        elif card.cmc == 3:
            cat4Sum = cat4Sum + 1

        elif card.cmc == 4:
            cat5Sum = cat5Sum + 1

        elif card.cmc == 5:
            cat6Sum = cat6Sum + 1

        elif card.cmc == 6:
            cat7Sum = cat7Sum + 1

        elif card.cmc == 7:
            cat8Sum = cat8Sum + 1

        else:
            cat9Sum = cat9Sum + 1

    data = [cat1Sum, cat2Sum, cat3Sum, cat4Sum, cat5Sum, cat6Sum, cat7Sum, cat8Sum, cat9Sum]

    return render_template('manaCurveChart.html', data=data)
