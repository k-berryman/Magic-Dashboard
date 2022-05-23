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
