from flask_wtf import FlaskForm
from wtforms import FloatField, StringField
from wtforms.validators import InputRequired, Optional, Length, Email

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
