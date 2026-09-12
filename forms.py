

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, EmailField, FieldList, FormField, HiddenField, IntegerField, PasswordField, RadioField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    register = SubmitField("Register")