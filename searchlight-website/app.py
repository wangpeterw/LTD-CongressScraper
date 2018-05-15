#!/usr/bin/env python

import flask
from flask import Response, request, send_file, flash
import json
import sqlite3
import csv
from config import Config
from contactform import ContactForm


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
# from flask_wtf.csrf import CSRFProtect
# from flask_mail import Message, Mail

app = flask.Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

# mail = Mail()
# app.secret_key = 'development key'
#
# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_USERNAME"] = 'contact@example.com'
# app.config["MAIL_PASSWORD"] = 'your-password'
#
# mail.init_app(app)

@app.route('/')
def index():
	"""
	Displays the home page that leads users into different pages
	"""
	return flask.render_template('index.html')

@app.route('/about')
def about():
	return flask.render_template('about.html')

@app.route('/process')
def process():
	return flask.render_template('process.html')

@app.route('/team')
def team():
	return flask.render_template('team.html')

# @app.route('/contact', methods=["GET", "POST"])
# def contact():

# 	if request.method == 'POST':
# 		email = request.form.get('email')
# 		name = request.form.get('message')
# 		subject = request.form.get('subject')
# 		message = request.form.get("message")
# 		#send_email(message, reply_to)
# 		return flask.render_template('contact.html', success=True)
# 	else:

		# return flask.render_template('contact.html', success=False, message_type=message_type)


# 	return flask.render_template('contact.html', message_type=message_type)

@app.route('/contact', methods=["GET", "POST"])
def contact():
	form = ContactForm()
	message_type = ["More Information about Goodly Labs",
	"Potential Errors in the Dataset", "Suggestions", "Questions and Concerns", "Other"]
	if form.validate_on_submit():

		email = request.form.get('email')
		name = request.form.get('name')
		subject = request.form.get('subject')
		message = request.form.get("message")
		body = "Name: " + name + "\nEmail: " + email + "\n\nSubject: " + subject + "\n\nBody: " + message + "\n\n"

		#print("RETRIEVED")

		msg_for_us = Message(subject="Searchlight Contact Form Submission", sender=app.config.get("MAIL_USERNAME"),
					recipients=["omkar.waingankar@berkeley.edu", "nalinchopra123@gmail.com"],
					body=body)
		mail.send(msg_for_us)

		msg_for_sender = Message(subject="Searchlight Contact Form Receipt", sender=app.config.get("MAIL_USERNAME"),
					recipients=[email],
					body="Hi " + name + ",\n\n" + "Thanks for connecting with us. " +
					"We'll be sure to get back in touch with you as soon as possible!\n\n" +
					"Contact Form Receipt: \n\n" + body +
					"Best,\nThe Searchlight Team")

		mail.send(msg_for_sender)

		#print("MESSAGE SENT BY " + name)

		return flask.render_template('contact.html', title='Submitted', success=True)

	return flask.render_template('contact.html', title='Contact Us', form=form, message_type=message_type, success=False)

@app.route('/query')
def speakers():
	"""
	This is how arguments are passed from the View to this controller
	The get request can look like this:
	/speakers?name=rubio&format=csv
	This tells the controller to get all speeches by rubio in a csv format
	/speakers?name=rubio
	the url above just tells the controller to get speeches by rubio and display them
	/speakers
	The url above simply asks for all speeches to be displayed
	/speakers?format=csv
	Asks for all speeches to be made available in csv format
	"""

	format_ = request.args.get("format", None)

	num_get_requests = 0

	speaker_firstname_raw = request.args.get("firstname", "")
	speaker = request.args.get("surname", "")

	speaker_surname = speaker.upper()
	try:
		speaker_firstname = first_name_format(speaker_firstname_raw)
		print(speaker_firstname)
	except:
		speaker_firstname = speaker_firstname_raw

	district_query = request.args.get("district", "")
	state_query = request.args.get("state", "")
	party_query = request.args.get("party", "")
	type_query = request.args.get("type", "")

	month = request.args.get("month", "")
	day = request.args.get("day", "")
	year = request.args.get("year", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	#Query that gets the records that match the query
	# all_records_query = "SELECT speakers_2017_Jan_3_to_10.session_title as title, \
	#  			speakers_2017_Jan_3_to_10.date as date, speakers_2017_Jan_3_to_10.speech_text as text, \
	# 			speakers_2017_Jan_3_to_10.last_name as surname, speakers_2017_Jan_3_to_10.first_name as first_name, \
	# 			 FROM speakers_2017_Jan_3_to_10 inner join speeches_2017_Jan_3_to_10 on \
	# 			speakers_2017_Jan_3_to_10.speaker_id = speeches_2017_Jan_3_to_10.speaker_id \
	# 			%s %s;"

	all_records_query = "SELECT * FROM allspeakers \
						inner join allspeeches on allspeeches.speaker_id = allspeakers.speaker_id \
						%s %s;"

	# "SELECT * FROM allspeakers \
	# 					inner join allspeeches on allspeeches.speaker_id = allspeakers.speaker_id \
	# 					%s %s;"
	records = []
	records_total = []
	where_clause = ""
	where_array = []
	condition_tuple = []
	if speaker_surname or speaker_firstname or district_query or state_query or party_query or type_query or month or day or year:
		where_clause += "where "
		if speaker_surname:
			where_array.append("last_name like ? ")
			condition_tuple.append("%" + speaker_surname + "%")
		if speaker_firstname:
			where_array.append("first_name like ? ")
			condition_tuple.append("%" + speaker_firstname_raw + "%")
		if type_query:
			where_array.append("type = ? ")
			condition_tuple.append(str(type_query))
		if party_query:
			where_array.append("party = ? ")
			condition_tuple.append(str(party_query))
		if state_query:
			where_array.append("state = ? ")
			condition_tuple.append(str(state_query))
		if day:
			where_array.append("day = ? ")
			condition_tuple.append(str(day))
		if year:
			where_array.append("year = ? " if len(year) > 2 else "")
			condition_tuple.append(str(year))
		if month:
			where_array.append("month = ? ")
			condition_tuple.append(str(month))
		if district_query:
			where_array.append("district = ? ")
			condition_tuple.append(str(district_query))

		where_clause += "and ".join(where_array)
		condition_tuple = tuple(condition_tuple)
		limit_statement = ""
		all_records_query = all_records_query % (where_clause, limit_statement)
		print(all_records_query)
		print(condition_tuple)

		cursor.execute(all_records_query, condition_tuple)
		records_total = cursor.fetchall()

		# "LIMIT 20" if format_ != "csv" else ""
		records = records_total[:20]
		connection.close()



	if format_ == "csv":
		return download_csv(records, "speeches_%s.csv" % (speaker_surname.lower()))
	else:
		years = [x for x in range(2018, 2016, -1)]
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		days = [x for x in range(1, 32)]
		parties = ['R', 'D', 'I']
		states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
		"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
		"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
		"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
		"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
		districts = [x for x in range(1, 54)]
		types = ['SENATOR', 'REPRESENTATIVE', 'DELEGATE']

		selected_dict = {}
		selected_dict["year"] = int(year) if year else None
		selected_dict["month"] = month if month else None
		selected_dict["day"] = int(day) if day else None
		selected_dict["state"] = state_query if state_query else None
		selected_dict["party"] = party_query if party_query else None
		selected_dict["type"] = type_query if type_query else None
		selected_dict["district"] = int(district_query) if district_query else None
		print(selected_dict)

		return flask.render_template('speaker.html', records=records, no_of_records=len(records_total),
			speaker_firstname=speaker_firstname_raw, speaker_surname=speaker,
			years=years, months=months, days=days, states=states, parties=parties, districts=districts,
			types=types, selected_dict = selected_dict, date_format=date_format)

########################################################################
# The following are helper functions. They do not have a @app.route decorator
########################################################################
def dictionary_factory(cursor, row):
	"""
	This function converts what we get back from the database to a dictionary
	"""
	d = {}
	for index, col in enumerate(cursor.description):
		d[col[0]] = row[index]
	return d

def download_csv(data, filename):
	"""
	Pass into this function, the data dictionary and the name of the file and it will create the csv file and send it to the view
	"""
	header = data[0].keys() #Data must have at least one record.
	with open('downloads/' + filename, "w+") as f:
		writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for row in data:
			writer.writerow(list(row.values()))

	#Push the file to the view
	return send_file('downloads/' + filename,
				 mimetype='text/csv',
				 attachment_filename=filename,
				 as_attachment=True)

def first_name_format(name):
	first_char = name[0]
	rest_name = name[1:]
	return first_char.upper() + rest_name.lower()
# function to make first name Rubio

def date_format(month, day, year):
	month_dict = {'January' : '1', 'February' : '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6', 'July': '7', 'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}
	month_str = month_dict[month]
	return month_str + '/' + str(day) + '/' + str(year)
if __name__ == '__main__':
	app.debug=True
	app.run()
