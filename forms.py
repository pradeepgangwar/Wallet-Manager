from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import *

class LoginForm(Form):
	username = TextField('Username', validators = [DataRequired()])
	password = PasswordField('Password', validators = [DataRequired()])

class SignupForm(Form):
	username = TextField('Username', validators = [DataRequired(), Length(min=3, max=10, message='Must be 3 to 10 characters long')])
	password = PasswordField('Password', validators = [DataRequired(), EqualTo('confirm', message='Passwords Do Not match'),Length(min=4, max=10, message='Must be 4 to 10 characters long')])
	email = TextField('Email', [DataRequired(), Email()])
	confirm  = PasswordField('Repeat Password', [DataRequired()])