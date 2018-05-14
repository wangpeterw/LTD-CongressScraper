import os
from flask_mail import Mail, Message

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'n320dNK3j2kfnWKn98dsnlJ8lWe34CV089Wm'
    mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    # "MAIL_USERNAME": os.environ['EMAIL_USER'],
    # "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
    "MAIL_USERNAME": 'email_user',
    "MAIL_PASSWORD": 'email_password'
	}