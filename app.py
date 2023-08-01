import random
import logging

from chart import chart_render_seaborn_chart
from google_sheets import manager, data_manager
from utils import validate_session_id
from config import SECRET_KEY
from constants import INVALID_PASSWORD, SESSION_ID_EXISTS, \
	SESSION_ID_MUST_BE_DIGIT, INSERT_FOUR_DIGIT_NUMBER, SESSION_ID_NOT_EXIST

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = SECRET_KEY
app.logger.setLevel(logging.DEBUG)  # DELETE


@app.route('/')
def index():
	return render_template('index.html')

##################
# Trainer routes #
##################


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':  # DELETE
		if request.form['password'] != '1234':
			error = INVALID_PASSWORD
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

			if data_manager.get_wk_by_name(session_id) is not None:
				error = SESSION_ID_EXISTS
				return render_template('new_session.html', session_id=session_id, ethnicities=ethnicities, error=error)
			else:
				manager.add_session(session_id, session_description)
				manager.create_session_wk(session_id)
		else:
			error = SESSION_ID_MUST_BE_DIGIT
			return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=False, error=error)

	return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=form_submitted, error=error)

@app.route('/analyze_session', methods=['GET', 'POST'])
def analyze_session():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']

		if not validate_session_id(session_id):
			error = INSERT_FOUR_DIGIT_NUMBER
		else:
			session_exists = data_manager.get_wk_by_name(session_id)

			if not session_exists:
				error = SESSION_ID_NOT_EXIST
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

##################
# Trainee routes # 
##################

@app.route('/experience_menu')
def experience_menu():
	return render_template('experience_menu.html')

@app.route('/video_login', methods=['GET', 'POST'])
def video_login():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']

		if not validate_session_id(session_id):
			error = INSERT_FOUR_DIGIT_NUMBER
		else:
			session_exists = data_manager.get_wk_by_name(session_id)

			if not session_exists:
				error = SESSION_ID_NOT_EXIST
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
	session_id = session.get('session_id')
	response_time = round(float(data['timestamp']), 2)
	response_time = str(response_time).replace(',', '.')

	try:
		manager.add_record(session_id, response_time)
		return 'Time saved', 200
	except ValueError as ve:
		app.logger.error('Error when saving response time: %s', ve)
		return str(ve), 400
	except Exception as e:
		app.logger.error('Error when saving response time: %s', e)
		return 'Internal server error', 500
	
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if request.method == 'POST':
		feedback = request.form['feedback']
		session_id = session.get('session_id')

		try:
			manager.add_feedback(session_id, feedback)

			return render_template('feedback.html', message='Thank you for your feedback.', form_submitted=True), 200
		except ValueError as ve:
			app.logger.error('Error when saving feedback: %s', ve)
			return str(ve), 400
		except Exception as e:
			return render_template('feedback.html', message='Unable to save your feedback.'), 500
	else:
		return render_template('feedback.html')


if __name__ == '__main__':
	socketio.run(app)
