"""test Flask with this"""

from flask import Flask, render_template, jsonify, redirect
from forms import AddForm, RegisterForm, LoginForm
import requests

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'TESTINGGG'

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
        #user = User(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        #db.session.add(user)
        #db.session.commit()

        # redirect
        return redirect('/success')
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    # if it's a request with a valid CSRF Token
    if form.validate_on_submit():
        # retrieve data from form
        username = form.username.data
        password = form.password.data

        # verification...?

        # redirect
        return redirect('/secret')

    else:
        return render_template("login.html", form=form)




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
