"""test Flask with this"""

from flask import Flask, render_template
from forms import AddForm

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'TESTINGGG'

@app.route('/')
def home():
    return "Hello Worlds"

@app.route('/form', methods=["GET", "POST"])
def form():
    form = AddForm()

    # if it's a post request with a valid CSRF Token
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        print(name, price)
        return redirect('/answer')

    else:
        return render_template("index.html", form=form)
