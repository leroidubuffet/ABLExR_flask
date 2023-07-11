# Standard libraries
import random
from datetime import datetime
import logging
import io
import base64

# Third-party libraries
from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_socketio import SocketIO, emit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# App libraries
from chart import render_seaborn_chart as chart_render_seaborn_chart
from google_sheets import get_s_data, add_record, add_session, add_feedback, get_last_added_wk, get_wk_by_name, create_session_wk, get_rt_data, get_s_data, get_f_data
from utils import map_ethnicity, inverse_ethnicity_mapping, validate_session_id

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = '0987654321' # DEBUG
app.logger.setLevel(logging.DEBUG) # DEBUG

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['password'] != '1234':
			error = 'Invalid password. Please try again.'
		else:
			return redirect(url_for('trainer_dashboard'))
	return render_template('login.html', error=error)

@app.route('/trainer_dashboard')
def trainer_dashboard():
	return render_template('trainer_dashboard.html')

@app.route('/new_session', methods=['GET', 'POST'])
def new_session():
	ethnicities = ['random', 'black', 'latino', 'white']
	session_id = None
	form_submitted = False
	error = None

	if request.method == 'POST':
		form_submitted = True
		race_digit = None
		ethnicity = request.form['ethnicity']
		session_description = request.form['session_description']
		if ethnicity == 'random':
			ethnicity_id = random.choice([1, 2, 3])
			race_digit = str(ethnicity_id)
		else:
			ethnicity_mapping = {
				'black': 1,
				'latino': 2,
				'white': 3
			}
			ethnicity_id = ethnicity_mapping.get(ethnicity)
			if ethnicity_id is not None:
				race_digit = str(ethnicity_id)

		user_session_id = request.form['session_id']
		if user_session_id and user_session_id.isdigit() and len(user_session_id) <= 3 and race_digit is not None:
			session_id = race_digit + user_session_id.zfill(3)  # Combine race digit and user session ID

			# Check if the session already exists
			if get_wk_by_name(session_id) is not None:
				error = 'Session ID already exists. Please try a different ID.'
				return render_template('new_session.html', session_id=session_id, ethnicities=ethnicities, error=error)
			else:
				# Save the record to Google Spreadsheet
				add_session(session_id, session_description)
				create_session_wk(session_id)

	return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=form_submitted, error=error)

# Convert the 'session_id' and 'ethnicity' columns to integer
df_s = get_s_data()
df_s['session_id'] = df_s['session_id'].astype(int)

df_s['ethnicity'] = df_s['ethnicity'].map(inverse_ethnicity_mapping).astype(int)

@app.route('/analyze_session', methods=['GET', 'POST'])
def analyze_session():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']
		print("Analyza session.Session ID:", session_id)  #  DEBUG

		if not session_id.isdigit() or len(session_id) != 4:
			error = 'Insert a four digit number please.'
		else:
			# Split the session_id into ethnicity and session_id
			ethnicity = int(session_id[0])
			session_id = int(session_id[1:])

			# Query the table to check if the session ID exists
			session_exists = df_s[(df_s['session_id'] == session_id) & (df_s['ethnicity'] == ethnicity)].shape[0] > 0

			if not session_exists:
				error = 'That session ID does not exist.'
			else:
				return redirect(url_for('render_seaborn_chart'))        

	return render_template('analyze_session.html', error=error)

@app.route('/analysis/<session_id>', methods=['GET', 'POST'])
def render_seaborn_chart(session_id):
	return chart_render_seaborn_chart(request)

@app.route('/experience_menu')
def experience_menu():
	# Retrieve the last active session_id from the Google Spreadsheet
	df_s = get_s_data()
	if not df_s.empty:
		last_session_id = df_s['session_id'].iloc[-1]
		session['session_id'] = int(last_session_id)
		print("Experience.Session ID:", last_session_id)  # DEBUG
	else:
		print("No sessions found.")  #  DEBUG
	return render_template('experience_menu.html')

@app.route('/waiting_room')
def waiting_room():
	return render_template('waiting_room.html')

@app.route('/ar_vr')
def ar_vr():

	# Retrieve the last saved session_id from the Google Spreadsheet
	df_s = get_s_data()
	session_id = str(df_s['session_id'].iloc[-1])

	# Convert the int64 to a regular int before storing it in the session
	session['session_id'] = int(session_id)
	print("AR/VR.Session ID:", session_id)  #  DEBUG
	
	return render_template('ar_vr.html', pairing_id=session_id)

@app.route('/video')
def video():
	return render_template('video.html')

@app.route('/save_responsetime', methods=['POST'])
def save_responsetime():
	data = request.get_json()
	print('Data:', data) # DEBUG
	response_time = round(float(data['timestamp']), 2)
	session_id = session['session_id']  # Get the session_id from the session
	print("Save response time.Session ID:", session_id)  #  DEBUG

	try:
		# Add the record to the DataFrame and Google Spreadsheet
		add_record(session_id, response_time)
		return 'Time saved'
	except Exception as e:
		# Handle the exception, you can log the error or return an error message
		app.logger.error('Error when saving response time: %s', e)
		return 'Unable to save your time.'
	
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		feedback = request.form['feedback']
		session_id = session.get('session_id')
		print("Feedack.Session ID:", session_id)  #  DEBUG

		try:
			# Add the feedback to the Google Sheet
			add_feedback(session_id, feedback)

			return render_template('feedback.html', message='Thank you for your feedback.')
		except Exception as e:
			# Handle the exception, you can log the error or return an error message
			return render_template('feedback.html', message='Unable to save your feedback.')
	else:
		# Render the feedback form
		return render_template('feedback.html')

if __name__ == '__main__':
	socketio.run(app)
