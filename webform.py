from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField, EmailField, IntegerField
from wtforms.validators import DataRequired


class AdminForm(FlaskForm):
	username = StringField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	submit = SubmitField("Submit")

class UserForm(FlaskForm):
	name = StringField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	submit = SubmitField('Sign up')
	
class LoginForm(FlaskForm):
	email = EmailField(validators=[DataRequired()])
	password = PasswordField( validators=[DataRequired()])
	submit = SubmitField('Sign in')
	
class OrderForm(FlaskForm):
	quantity = IntegerField(validators=[DataRequired()])
	comment = TextAreaField()
	location = TextAreaField(validators=[DataRequired()])
	submit = SubmitField('Send Order')
	
class MealForm(FlaskForm):
	dish = TextAreaField(validators=[DataRequired()])
	price = IntegerField(validators=[DataRequired()])
	image = FileField()
	submit = SubmitField("Add")
	
class ChatForm(FlaskForm):
	text = TextAreaField()
	image = FileField()
	submit = SubmitField("Send")