#!/usr/bin/env python

import flask
from flask import Response, request, send_file
import json
import sqlite3
import csv

# Create the application.
app = flask.Flask(__name__)

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

@app.route('/contact')
def contact():
	return flask.render_template('contact.html')

@app.route('/database')
def database():
	return flask.render_template('database.html')

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

	all_records_query = "SELECT * FROM speakers_2017_Jan_3_to_10 \
						inner join speeches_2017_Jan_3_to_10 on speakers_2017_Jan_3_to_10.speaker_id = speeches_2017_Jan_3_to_10.speaker_id \
						%s %s;"
	records = []
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
		limit_statement = "LIMIT 20" if format_ != "csv" else ""
		all_records_query = all_records_query % (where_clause, limit_statement)
		print(all_records_query)
		print(condition_tuple)

		cursor.execute(all_records_query, condition_tuple)
		records = cursor.fetchall()
		print(records)
		connection.close()



	#if speaker:
	#	where_clause += " speaker.surname = ? " if speaker else ""
	#if year and speaker:
	#	where_clause += " and "
	#if year:
	#	where_clause += " hearing.date like ? " if len(year)>2 else ""



	# if speaker and year:
	# 	cursor.execute(all_records_query ,(speaker.lower(), "%"+ year))
	# elif speaker:
	# 	cursor.execute(all_records_query ,(speaker.lower(),))
	# elif year:
	# 	cursor.execute(all_records_query ,("%"+ year,))
	# else:
	# 	cursor.execute(all_records_query)
	# records = cursor.fetchall()

	# #Query to count the number of records
	# count_query =  "SELECT count(*) as count FROM hearing inner join speech on \
	# 			speech.hearing_id = hearing.hearing_id inner join speaker \
	# 			on speaker.speech_id = speech.speech_id %s;"
	# count_query = count_query % (where_clause)
	# if speaker and year:
	# 	cursor.execute(count_query, (speaker.lower(), "%"+ year))
	# elif year:
	# 	cursor.execute(count_query, ("%"+ year,))
	# elif speaker:
	# 	cursor.execute(count_query, (speaker.lower()))
	# else:
	# 	cursor.execute(count_query)



	#There's a lot of if else going on here but I will send a better solution for you guys to work with
	#no_of_records = cursor.fetchall()
	#connection.close()
	#Send the information back to the view
	#if the user specified csv send the data as a file for download else visualize the data on the web page
	if format_ == "csv":
		return download_csv(records, "speeches_%s.csv" % (speaker.lower()))
	else:
		years = [x for x in range(2018, 1995, -1)]
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		days = [x for x in range(1, 32)]
		parties = ['R', 'D', 'I']
		states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
		"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
		"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
		"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
		"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
		districts = [x for x in range(1, 436)]
		types = ['SENATOR', 'REPRESENTATIVE', 'DELEGATE']
		selected_year = int(year) if year else None
		return flask.render_template('speaker.html', records=records, no_of_records=0,
			speaker=speaker, years=years, months=months, days=days, states=states, parties=parties, districts=districts,
			types=types, selected_year=selected_year)

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
	month_dict = {'January' : '01', 'February' : '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}
	month_str = month_dict['month']
	return month_str + '/' + str()
if __name__ == '__main__':
	app.debug=True
	app.run()
