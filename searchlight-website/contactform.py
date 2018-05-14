from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired("Invalid Name")])
    email = StringField('Email', validators=[DataRequired("Invalid Email Address"), Email("Invalid Email Address")])
    subject = StringField('Subject', validators=[DataRequired("Invalid Subject")])
    message = StringField('Message', validators=[DataRequired("Invalid Message")])
    submit = SubmitField('Send')