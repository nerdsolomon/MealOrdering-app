from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField, EmailField, IntegerField
from wtforms.validators import DataRequired

	
class Forms(FlaskForm):
    string = StringField(validators=[DataRequired()])
    number = IntegerField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    text = TextAreaField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    file = FileField()
    submit = SubmitField("Done")