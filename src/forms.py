import os

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField
    )

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)
from src.models import Users

# Flask Login
class RegisterForm(FlaskForm):
    def validate_username(self, check_user):
        user = Users.query.filter_by(name=check_user.data).first()
        if user:
            raise ValidationError("User already exists! Register another user name.")

    def validate_email(self, check_email):
        email = Users.query.filter_by(email=check_email.data).first()
        if email:
            raise ValidationError(
                "E-mail already exists! Register another user E-mail."
            )

    def validate_password(self, check_password):
        #password = Users.query.filter_by(password=check_password.data).first()
        #if password:
        #    raise ValidationError(
        #        "Password already exists! Register another user Password."
        #    )
        pass

    name = StringField(
        label="Username:", validators=[Length(min=2, max=30), DataRequired()]
    )
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    password = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password_conf = PasswordField(
        label="Confirmation Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")

class LoginForm(FlaskForm):
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])
    password = PasswordField(label="Senha:", validators=[DataRequired()])
    submit = SubmitField(label="Log In")

class UserProfile(FlaskForm):
    name = StringField(label="Username:", validators=[Length(min=4, max=24), DataRequired()])
    email = StringField(label="E-mail:", validators=[Email(), DataRequired()])

    old_password = PasswordField(
        label="Old password:"
    )
    new_password = PasswordField(
        label="New password:"
    )
    confirm_password = PasswordField(
        label="Confirm password:"
    )
    GeminiAI = StringField(label="GeminiAI:")

    submit = SubmitField(label="Confirm changes")