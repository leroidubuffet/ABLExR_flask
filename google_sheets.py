from datetime import datetime
import logging

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from constants import CREDENTIALS_FILE, DOCUMENT_NAME
from utils import map_ethnicity

# Configure logging
logging.basicConfig(level=logging.INFO)


def authenticate(CREDENTIALS_FILE):
	"""Authenticate using the provided credentials file"""
	scope = ["https://spreadsheets.google.com/feeds",
			"https://www.googleapis.com/auth/spreadsheets",
			"https://www.googleapis.com/auth/drive.file",
			"https://www.googleapis.com/auth/drive"]

	creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
	return gspread.authorize(creds)

# Google Sheets setup
gc = authenticate(CREDENTIALS_FILE)
gs = gc.open(DOCUMENT_NAME)		# open document
wk_rt = gs.get_worksheet(0) 	# reaction time spreadsheet
wk_s = gs.worksheet('sessions')	# session spreadsheet
wk_f = gs.worksheet('feedback') # feedback spreadsheet

def get_ethnicity_by_session_id(session_id):
	worksheet = get_wk_by_name('sessions')

	if worksheet is None:
		return 'Sheet not found'

	# Convert session_id to string
	session_id = str(session_id)

	# Find all cells matching session_id
	matching_cells = worksheet.findall(session_id)

	if not matching_cells:
		return 'Session not found'

	# Get the first matching cell (assuming session_id is unique)
	cell = matching_cells[0]

	# Fetch the entire row of data
	row = worksheet.row_values(cell.row)

	# Fetch ethnicity    
	ethnicity = row[1]

	if not ethnicity:
		return 'Ethnicity not found'

	return ethnicity


def get_wk_by_name(session_id):
	try:
		return gs.worksheet(session_id)
	except gspread.exceptions.WorksheetNotFound:
		return None

def create_session_wk(id):
	wk = gs.add_worksheet(str(id), 0, 3)
	wk.append_row(["ethnicity", "reaction_t", "timeStamp"])
	return wk

def add_session(session_id, session_description):
	ethnicity_code = int(session_id[0])
	ethnicity = map_ethnicity(ethnicity_code)
	record = [session_id, ethnicity, session_description]
	wk_s.append_row(record, value_input_option='USER_ENTERED')

def get_rt_data_for_session(session_id):
	wk = get_wk_by_name(session_id)
	
	if wk is None:
		return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t', 'timeStamp'])
	
	records = wk.get_all_records()
	if records:
		return pd.DataFrame(records)
	else:
		return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t', 'timeStamp'])

def add_record(session_id, reaction_t):
	try:
		session_id = str(session_id)
		ethnicity_code = int(session_id[0])
	except ValueError:
		app.logger.error("Error converting session ID")
		return
	ethnicity_code = int(session_id[0])
	ethnicity = map_ethnicity(ethnicity_code)
	now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
	record = [ethnicity, reaction_t, now]
	
	wk = get_wk_by_name(session_id)
	
	if wk is None:
		wk = create_session_wk(session_id)
	
	wk.append_row(record)




def add_feedback(session_id, feedback):
	try:
		session_id = str(session_id)
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		record = [session_id, ethnicity, feedback]
		wk_f.append_row(record, value_input_option='USER_ENTERED')
	except Exception as e:
		app.logger.error('Error when adding feedback: %s', e)