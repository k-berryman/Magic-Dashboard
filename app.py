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
    data=[]

    # Get deck cards
    deckName = session['sessionDeckName']
    commander = Card.query.filter_by(name=deckName).first()
    deckCards = Card.query.filter_by(deck_id = commander.deck_id).all()

    for card in deckCards:
        data.append(card.price)

    return render_template('expenseChart.html', data=data)


@app.route('/manaCurveChart', methods=["GET", "POST"])
def manaCurveChart():
    return render_template('manaCurveChart.html')
