from flask_wtf import FlaskForm
from wtforms import FloatField, StringField
from wtforms.validators import InputRequired, Optional, Length, Email
from wtforms.fields import PasswordField


class AddCardForm(FlaskForm):
    """Add Card Form"""

    cardName = StringField(
      "Card Name",
      validators=[InputRequired()])


class RegisterForm(FlaskForm):
    """Register Form"""

    name = StringField("Name",
        validators=[
            InputRequired("Name can't be blank"),
            Length(min=1, max=50, message="Name must be 50 characters or less")])

    email = StringField("Email",
        validators=[
            InputRequired("Email can't be blank"),
            Email("Please enter a valid email"),
            Length(min=1, max=50, message="Email must be 50 characters or less")])

    username = StringField("Username",
        validators=[
            InputRequired("Username can't be blank"),
            Length(min=1, max=25, message="Username must be 25 characters or less")])

    password = PasswordField("Password",
        validators=[
            InputRequired("Password can't be blank")])


class LoginForm(FlaskForm):
    """Login Form"""

    username = StringField("Username",
        validators=[
            InputRequired("Username can't be blank"),
            Length(min=1, max=25, message="Username must be 25 characters or less")])

    password = PasswordField("Password",
        validators=[
            InputRequired("Password can't be blank")])
