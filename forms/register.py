from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField("login", validators=[DataRequired()])
    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    password_again = PasswordField("password again", validators=[DataRequired()])
    tg_username = StringField("telegram_username")
    submit = SubmitField("submit")