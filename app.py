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
import gspread

credentials = {
  "type": "service_account",
  "project_id": "tidy-gravity-349514",
  "private_key_id": "2d2d47fb47ddfb4ec6c2fa7beacdd8fe785f998e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0Bg21E6axY3fb\nww1iZnNG7zEc0D6Wy3lqsCSgQBnyb6PQcuMfAwK+4ZPDWh0dyGJ3nE6lHnn/IBrg\nsIFxBbUh5oZOwfaN1A9GU2/QDNiUNeJ3i7ba4mN1URqUpixQZFXYJ3jGN1bNJevl\npfkXXMx+9o0qXN5ZHKLso7K36WFZZdzRcWVDtyQskmE6kyVGUAQak/dWY0ZVMYFG\nsa/qnxvfRz57LrowzDFaenv0yp6/6vL5jyACoO/7BuJu36l43QLpDj9dC8dnlgO0\nZt05TjikSEzi/FnGQrK6BBYIZUdwxGqvFMyehbp/KV0YN1d9tvYnc80uSSkUzsYD\n283z6GD1AgMBAAECggEAA44gDKyp7NRkTFJ+i+wuiB7WpzVEmylDCVSXsJN7f7Jt\nN4NhUV43mmnth1za+NjZeve7BN9EdQGfDkNmFwOQF26MRfdmJVhkAdVJfsAWMd0b\njxVTA+EXKjyzC+75LpBAsr9azv1OSUhfr34W3HuAbVx0nrrNSFC8tfQopiGlgsSr\n4MqrHdR+qXaWHof1H4ypYVY8uWSd5bXXJ/H4joNcpyIQ2KyJSpAmhuXEDAu6eaKA\nNwM6w43ModnaP+pWtAoiVSTlnsy5Eaw2c0zCrfqXq83Zft0uZMPRU5IWpYBArV4C\neF7znLal8fyNyAeMbjFQbOq6Xwxm2C+WFUedDUAl+QKBgQD7rcjdFxpCcm7Llsso\nqOIDaKmoXF3dzANciUULJleu1Z+uwXd5caRpStRrgIONZeEqqCHDSLVaU4QHg4nN\nOUA38NBcN4Q/G87n/9Fw+D9AbbYDKTrPFDFgN/KcyyXLnlfY6oNBXeaqhTiIxokD\nHV1m7Xt2monPr5ixt2k9w9maqQKBgQC3HVHQ0NysVHifD7bYw0BsmBRUF/gyhZKm\nvE+3HZnTTNzSlUt1vKUePflyc26S4xFHczZR1zs1/UJztvNusUeRNQTrKv/3xpqg\n+COxb6Kx6pzo6SSjFbdOYFxMEv0WU/HeMODdQahggL1/TIW9T1cc89IB3WwyQ3Nx\nPZ+L0EivbQKBgBB2ksAbpcUY9TRuHcYAHiC49PglaqJ6mPGxrQmIrY2rPbHRx/3y\nuB2HHpQVqQVT18HRk7vRgsNw2R8gtJ/vEctW/lo563WxXPyCGHI6WvDc/F4CkW1A\nVeaEYmNtSoCiT/7JgGKDQPaAlm0kB4xjnFuCR2Q/waoLQ4LEi6bVq+NZAoGAOEOZ\nBQl4FLdrzKv+acIsxHFCJcirqZJjSjooYEKHJmbCny3iXs3VCmLOh70yJ43/nC2p\nbiIs/lzQE1AOol90dwiMd1niBpcOohE8nmOH4RUOm34vlLCyfzGaioF3JGossjHg\nlft7qhNEpp2zpkR/ptTAHXSUrykMiqn9oO8htk0CgYBA3yB9DeatlSe9c3yUhzhe\nBeDEaOtXF7Mu/mR/AEzF4+UMI4g9syIQ40M3uEedBdgw2tmO2+HRl8n8giacLzok\nQJN3AE7zIxaRg4XwZ5XdoYtEgaEHHOA0iQv4uFtOwzyrRnJUHCw8lKcl238Cj1ek\nM7UmX5im0Vs7sDU5KDcv+g==\n-----END PRIVATE KEY-----\n",
  "client_email": "eys-445@tidy-gravity-349514.iam.gserviceaccount.com",
  "client_id": "106310523143023000697",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/eys-445%40tidy-gravity-349514.iam.gserviceaccount.com"
}

# Google Sheets setup
gc = gspread.service_account_from_dict(credentials)
gs = gc.open("ABLExR-DATA")		# open document
wk_rt = gs.get_worksheet(0) 	# reaction time spreadsheet
wk_s = gs.get_worksheet(1) 		# session spreadsheet
wk_f = gs.get_worksheet(2) 		# feedback spreadsheet

def get_rt_data():
	records = wk_rt.get_all_records()
	if records:
		return pd.DataFrame(records)
	else:
		return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t', 'timeStamp'])

def get_s_data():
	records = wk_s.get_all_records()
	if records:
		return pd.DataFrame(records)
	else:
		return pd.DataFrame(columns=['session_id', 'ethnicity', 'description'])

def get_f_data():
	records = wk_f.get_all_records()
	if records:
		return pd.DataFrame(records)
	else:
		return pd.DataFrame(columns=['session_id', 'ethnicity', 'feedback'])

df_rt = get_rt_data()
df_s = get_s_data()
df_f = get_f_data()

def add_record(session_id, reaction_t):
    session_id = str(session_id)  # Convert session_id to string
    ethnicity = int(session_id[0])
    id = int(session_id[1:])  # Extract digits 1 to 3 from session_id
    now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
    record = [id, ethnicity, reaction_t, now]
    df_rt.loc[len(df_rt)] = record
    wk_rt.update([df_rt.columns.values.tolist()] + df_rt.values.tolist())

def add_session(session_id, session_description):
	ethnicity = int(session_id[0])
	id = int(session_id[1:])  # Extract digits 1 to 3 from session_id
	record = [id, ethnicity, session_description]
	wk_s.append_row(record, value_input_option='USER_ENTERED')

def add_feedback(session_id, feedback):
	try:
		session_id = str(session_id)  # Convert session_id to string
		ethnicity = int(session_id[0])
		id = int(session_id[1:])  # Extract digits 1 to 3 from session_id
		record = [id, ethnicity, feedback]
		df_f.loc[len(df_f)] = record
		wk_f.update([df_f.columns.values.tolist()] + df_f.values.tolist())
	except Exception as e:
		app.logger.error('Error when adding feedback: %s', e)


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = '0987654321' # DEBUG store this key in an environment variable or a configuration file
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

	if request.method == 'POST':
		form_submitted = True
		race_digit = None
		ethnicity = request.form['ethnicity']
		session_description = request.form['session_description']
		print("ethnicity:", ethnicity)  # New print statement DEBUG
		print("Session Description:", session_description)  # New print statement DEBUG
		if ethnicity == 'random':
			ethnicity_id = random.choice([1, 2, 3])
			race_digit = str(ethnicity_id)  # Set race_digit here as well
		else:
			ethnicity_mapping = {
				'black': 1,
				'latino': 2,
				'white': 3
			}
			ethnicity_id = ethnicity_mapping.get(ethnicity)
			if ethnicity_id is not None:
				race_digit = str(ethnicity_id)

		print("Race Digit:", race_digit)  # New print statement DEBUG

		user_session_id = request.form['session_id']
		print("User Session ID:", user_session_id)  # New print statement DEBUG
		if user_session_id and user_session_id.isdigit() and len(user_session_id) <= 3 and race_digit is not None:
			session_id = race_digit + user_session_id.zfill(3)  # Combine race digit and user session ID
			print("Session ID:", session_id)  # New print statement DEBUG

			# Save the record to Google Spreadsheet
			add_session(session_id, session_description)

	return render_template('new_session.html', ethnicities=ethnicities, session_id=session_id, form_submitted=form_submitted)


# Convert the 'session_id' and 'ethnicity' columns to integer
df_s['session_id'] = df_s['session_id'].astype(int)
df_s['ethnicity'] = df_s['ethnicity'].astype(int)

@app.route('/analyze_session', methods=['GET', 'POST'])
def analyze_session():
	error = None
	if request.method == 'POST':
		session_id = request.form['session_id']
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


@app.route('/analysis', methods=['GET', 'POST'])
def render_seaborn_chart():
	# Generate your Seaborn chart here
	# Specify the dimension you want to replace
	if request.method == 'POST':
		dimension = request.form['dimension']
	else:
		dimension = 'Anger'
		
	# Load data from csv
	officer_df = pd.read_csv('datasets/OF_language.csv')
	driver_df = pd.read_csv('datasets/DF_language.csv')
	scene_df = pd.read_csv('datasets/O+D_F_language.csv')

	# Load the data from the Google Spreadsheet
	df_rt = get_rt_data()

	# Convert the 'session_ID' and 'ethnicity' columns to integer
	df_rt['session_ID'] = df_rt['session_ID'].astype(int)
	df_rt['ethnicity'] = df_rt['ethnicity'].astype(int)

	# Map the ethnicity numbers to their corresponding names
	ethnicity_mapping = {
		1: 'Black',
		2: 'Latino',
		3: 'White'
	}
	df_rt['ethnicity'] = df_rt['ethnicity'].map(ethnicity_mapping)

	# Filter the DataFrame to include only the desired ethnicity
	desired_ethnicity = 'Black'
	interventions_df = df_rt[df_rt['ethnicity'] == desired_ethnicity]

	plt.figure(figsize=(15, 5))

	plt.xlim(0, 180)  # Set x-axis limits to 0 and 180

	# Define a color palette with higher contrast
	color_palette = ["#6699CC", "#CC6666"]

	# Plot the Scene data
	scene_line = sns.lineplot(data=scene_df, x='BeginTime', y=dimension, color='none')

	# Plot the Officer data
	officer_line = sns.lineplot(data=officer_df, x='BeginTime', y=dimension, color=color_palette[0])

	# Plot the Driver data
	driver_line = sns.lineplot(data=driver_df, x='BeginTime', y=dimension, color=color_palette[1])

	# Interpolate the dimension value of the scene at the response times
	response_dimension = np.interp(interventions_df['reaction_t'], scene_df['BeginTime'], scene_df[dimension])

	# Add the scatter plot on top of the line plot
	colors = {desired_ethnicity: 'black'}
	scatter = plt.scatter(interventions_df['reaction_t'], response_dimension, c=interventions_df['ethnicity'].map(colors), s=10, zorder=10)

	# Create legend for the lines
	line_legend = [officer_line.lines[1], driver_line.lines[2]]

	# Create legend for the scatter plot
	scatter_legend = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=8)]

	# Combine the legends
	legend_handles = line_legend + scatter_legend
	legend_labels = ['Officer', 'Driver', 'Responses']

	# Add the combined legend to the plot
	plt.legend(handles=legend_handles, labels=legend_labels, loc='best', frameon=False, prop={'family':'Arial Narrow', 'size': 10})

	plt.title(f'Evolution of {dimension} Over Time', fontsize=20, fontname='Arial Narrow')
	plt.text(0.5, 0.95, f'POI ethnicity: {desired_ethnicity}', horizontalalignment='center', fontsize=11, transform=plt.gca().transAxes)
	plt.ylim(0, 1)# Set y-axis limits to 0 and 1

	# Set background color to white
	plt.gca().set_facecolor('white')

	# Set tick label font size and style
	plt.xticks(fontsize=12, fontname='Arial Narrow')
	plt.yticks(fontsize=12, fontname='Arial Narrow')

	# Set axis labels font size and style
	plt.xlabel('Time (s)', fontsize=10, fontname='Arial Narrow')
	plt.ylabel(f'{dimension} Level', fontsize=10, fontname='Arial Narrow')

	# Despine top and right axes
	sns.despine(top=True, right=True)

	# Save the figure to a BytesIO object
	bytes_image = io.BytesIO()
	plt.savefig(bytes_image, format='png')
	bytes_image.seek(0)

	# Convert the BytesIO object to a base64-encoded string
	base64_png = base64.b64encode(bytes_image.getvalue()).decode('ascii')

	# Pass the base64-encoded string to the template
	return render_template('analysis.html', chart_image=base64_png)


@socketio.on('ready')
def handle_ready(data):
	print('received ready: ' + str(data))
	emit('update', {'data': data['data'] + ' is connected'}, broadcast=True)

@app.route('/experience_menu')
def experience_menu():

	# Retrieve the last active session_id from the Google Spreadsheet
	df_s = get_s_data()
	last_session_id = df_s['session_id'].iloc[-1]

	# Convert the int64 to a regular int before storing it in the session
	session['session_id'] = int(last_session_id)

	return render_template('experience_menu.html')

@app.route('/waiting_room')
def waiting_room():
	return render_template('waiting_room.html')

@app.route('/ar_vr')
def ar_vr():

	# Retrieve the last saved session_id from the Google Spreadsheet
	df_s = get_s_data()
	ethnicity = df_s['ethnicity'].iloc[-1]
	pairing_id = df_s['session_id'].iloc[-1]
	session_id = int(str(ethnicity) + str(pairing_id).zfill(3))

	# Convert the int64 to a regular int before storing it in the session
	session['session_id'] = int(session_id)
	
	return render_template('ar_vr.html', pairing_id=session_id)

@app.route('/video')
def video():
	return render_template('video.html')

@app.route('/save_responsetime', methods=['POST'])
def save_responsetime():
    data = request.get_json()
    response_time = round(float(data['timestamp']), 2)
    session_id = session['session_id']  # Get the session_id from the session

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
		print(session_id)

		try:
			# Add the feedback to the Google Sheet
			add_feedback(session_id, feedback)

			return render_template('feedback.html', message='Thank you for your feedback')
		except Exception as e:
			# Handle the exception, you can log the error or return an error message
			return render_template('feedback.html', message='Unable to save your feedback.')
	else:
		# Render the feedback form
		return render_template('feedback.html')

if __name__ == '__main__':
	socketio.run(app)
