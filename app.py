# Standard libraries
import random
from datetime import datetime
import logging
import io
import base64

# Third-party libraries
from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_socketio import SocketIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# App libraries
from chart import chart_render_seaborn_chart
from google_sheets import add_record, add_session, add_feedback, get_wk_by_name, create_session_wk
from utils import validate_session_id

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = '0987654321' # DELETE
app.logger.setLevel(logging.DEBUG) # DELETE

@app.route('/')
def index():
	return render_template('index.html')

###############################
###		Trainer routes		###
###############################

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST': # DELETE
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
			session_id = race_digit + user_session_id.zfill(3)

			if get_wk_by_name(session_id) is not None:
				error = 'Session ID already exists. Please try a different ID.'
				return render_template('new_session.html', session_id=session_id, ethnicities=ethnicities, error=error)
			else:
				# Save the record to Google Spreadsheet
				add_session(session_id, session_description)
				create_session_wk(session_id)
		else:
			error = 'Session ID must be a 3 digit number.'
			return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=False, error=error)

	return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=form_submitted, error=error)

@app.route('/analyze_session', methods=['GET', 'POST'])
def analyze_session():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']

		if not validate_session_id(session_id):
			error = 'Insert a four digit number please.'
		else:
			session_exists = get_wk_by_name(session_id)

			if not session_exists:
				error = 'That session ID does not exist.'
			else:
				return redirect(url_for('render_seaborn_chart', session_id=session_id))        

	return render_template('analyze_session.html', error=error)


@app.route('/analysis/<session_id>', methods=['GET', 'POST'])
def render_seaborn_chart(session_id):
	if request.method == 'POST':
		dimension = request.form.get('dimension')
	else:
		dimension = 'Anger'
	return chart_render_seaborn_chart(session_id, dimension=dimension)

###############################
###		Trainee routes		### 
###############################

@app.route('/experience_menu')
def experience_menu():
	return render_template('experience_menu.html')

@app.route('/video_login', methods=['GET', 'POST'])
def video_login():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']

		if not validate_session_id(session_id):
			error = 'Insert a four digit number please.'
		else:
			session_exists = get_wk_by_name(session_id)

			if not session_exists:
				error = 'That session ID does not exist.'
			else:
				session['session_id'] = session_id
				return redirect(url_for('waiting_room', session_id=session_id))

	return render_template('video_login.html', error=error)

@app.route('/waiting_room/<session_id>')
def waiting_room(session_id):
	return render_template('waiting_room.html', session_id=session_id)

@app.route('/ar_vr')
def ar_vr():
	
	return render_template('ar_vr.html')

@app.route('/video')
def video():
	session_id = request.args.get('session_id')
	return render_template('video.html', session_id=session_id)

@app.route('/save_responsetime', methods=['POST'])
def save_responsetime():
	data = request.get_json()
	session_id = session.get('session_id')  # Get the session_id from the session object
	response_time = round(float(data['timestamp']), 2)
	response_time = str(response_time).replace(',', '.')

	try:
		add_record(session_id, response_time)
		return 'Time saved'
	except Exception as e:
		app.logger.error('Error when saving response time: %s', e)
		return 'Unable to save your time.'
	
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		feedback = request.form['feedback']
		session_id = session.get('session_id')

		try:
			add_feedback(session_id, feedback)

			return render_template('feedback.html', message='Thank you for your feedback.', form_submitted=True)
		except Exception as e:
			return render_template('feedback.html', message='Unable to save your feedback.')
	else:
		return render_template('feedback.html')

if __name__ == '__main__':
	socketio.run(app)
