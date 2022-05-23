# Magic The Gathering Stats Dashboard
Scryfall API docs - https://scryfall.com/docs/api

### Creating a new Flask App

-   Create a new virtual environment in my directory  `python3 -m venv env`
-   Activate the virtual environment  `source env/bin/activate`
-   Install Flask  `pip3 install Flask`
-   Create  `flask/`  folder and  `app.py`  in there
-   Add boilerplate code
```
"""test Flask with this"""

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'
```

-   `cd flask`
-  `flask run`  to run this locally on localhost:5000

---

### Setting up git & GitHub
`git init`
`git status`
Create a `.gitignore` and include `__pycache__`
`git add .`
`git commit -m "Initial commit"`

Create a new repo on GitHub
`git remote add origin https://github.com/k-berryman/Magic-Dashboard.git`
`git remote -v`
`git push origin master`

---

### Add WTForms
(with help from  [these instructions](https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html))

-   `pip3 install Flask-WTF`
-   `pip3 install flask-wtf`  just to double check
-   Create  `forms.py`
-   Add the following imports in  `forms.py`
```
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField
```
-   Configuring our form with the following

```
class AddForm(FlaskForm):
    """Form"""

    name = StringField("Snack Name")
    price = FloatField("Price in USD")
```

-   In  `app.py`,  `from forms import AddForm`
-   Start by rendering the form to the user which can be submitted via POST req
-   In  `app.py`

```
@app.route('/')
def home():
    form = AddForm()
    return render_template("index.html", form=form)
```
- Create `templates/index.html`
- In `index.html`,
```
<body>
  <h1>My Form</h1>
  <form action="" method="POST">
    {% for field in form
      if field.widget.input_type != 'hidden' %}
      <p>
        {{ field.label }}
        {{ field }}
      </p>
    {% endfor %}
    <button>Submit</button>
  </form>
</body>
```

- Update the route  `methods=["GET", "POST"]` in `app.py`

Now let's handle CSRF security
This part  `if field.widget.input_type != 'hidden'`  filters out CSRF Token in display

In `index.html` At the top of the form add `{{ form.hidden_tag() }} <!-- add type=hidden form fields -->` Make sure it's part of the form because we want it to be included in our POST req

Now we need to validate that token on the serverside. In  `app.py`,

```
@app.route('/form', methods=["GET", "POST"])
def form():
    form = AddForm()

    # if it's a post request with a valid CSRF Token
    if form.validate_on_submit():
        return redirect('/answer')

    else:
        return render_template("index.html", form=form)
```

Make sure to test with data for it to work properly

`validate_on_submit`  takes an empty form and fills it with data from the request

```
    # if it's a post request with a valid CSRF Token
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        print(name, price)
        return redirect('/answer')

```

Now we have the data!

Time to validate the data -- Throw friendly errors if it doesn't match ideal data format In  `forms.py`,  `from wtforms.validators import InputRequired, Optional, Email`

```
class AddForm(FlaskForm):
    """Form"""
    name = StringField(
      "Snack Name",
      validators=[InputRequired()])
    price = FloatField(
      "Price in USD",
      validators=[InputRequired()])
    quantity = FloatField(
      "Amount of Snack",
      validators=[InputRequired()])
```

`validate _on_submit` in `app.py` handles validating this

We want some error messages to render
In  `index.html`, in form,

```
      <p>
        {{ field.label }}
        {{ field }}

        {{% for err in field.errors %}}
          {{err}}
        {{% endfor %}}
      </p>
```

A secret key is required to use CSRF. In `app.py`,
```
# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'TESTINGGG'
```

This is what `index.html` should contain
```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Form</title>
</head>
<body>
  <h1>My Form</h1>
  <form method="POST">
    {{ form.hidden_tag() }} <!-- add type=hidden form fields -->
    {{ form.csrf_token }}

    {% for field in form
      if field.widget.input_type != 'hidden' %}
      <p>
        {{ field.label }}
        {{ field }}

        {% for err in field.errors %}
          {{ err }}
        {% endfor %}
      </p>
    {% endfor %}
    <button>Submit</button>
  </form>
</body>
</html>
```

Yay! WTForms is set up. Right now the values are from my last project, so we'll just update based on what input we need.

---
