from datetime import datetime
import logging

import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound, \
	CellNotFound, NoValidUrlKeyFound, APIError
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from constants import CREDENTIALS_FILE, DOCUMENT_NAME
from utils import map_ethnicity
from functools import wraps


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
gs = gc.open(DOCUMENT_NAME)		 # open document
wk_rt = gs.get_worksheet(0) 	 # reaction time worksheet
wk_s = gs.worksheet('sessions')	 # session worksheet
wk_f = gs.worksheet('feedback')  # feedback worksheet


# Exception handlig decorator
def handle_exceptions(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except SpreadsheetNotFound:
			logging.error(f"Spreadsheet not found for session_id: {args[1]}")
		except NoValidUrlKeyFound:
			logging.error(f"No valid URL key found for session_id: {args[1]}")
		except WorksheetNotFound:
			logging.error(f"Worksheet not found for session_id: {args[1]}")
		except CellNotFound:
			logging.error(f"Cell not found for session_id: {args[1]}")
		except APIError as e:
			logging.error(f"API Error when creating worksheet for session_id: {args[1]}. Error: {str(e)}")
		except Exception as e:
			logging.error(f"Error when creating session worksheet: {str(e)}")
		return None
	return wrapper


class GoogleSheetManager:
	def __init__(self, gs, wk_s, wk_f):
		self.gs = gs
		self.wk_s = wk_s
		self.wk_f = wk_f

	@handle_exceptions
	def get_wk_by_name(self, session_id):
		return self.gs.worksheet(session_id)

	@handle_exceptions
	def create_session_wk(self, session_id, rows=0, cols=3):
		wk = self.gs.add_worksheet(str(session_id), rows, cols)
		wk.append_row(["ethnicity", "reaction_t", "timeStamp"])
		return wk
	
	@handle_exceptions
	def add_session(self, session_id, session_description):
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		record = [session_id, ethnicity, session_description]
		self.wk_s.append_row(record, value_input_option='USER_ENTERED')

	@handle_exceptions
	def add_feedback(self, session_id, feedback):
		session_id = str(session_id)
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		record = [session_id, ethnicity, feedback]
		self.wk_f.append_row(record, value_input_option='USER_ENTERED')
	
	@handle_exceptions
	def add_record(self, session_id, reaction_t):
		session_id = str(session_id)
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
		record = [ethnicity, reaction_t, now]
	
		wk = self.get_wk_by_name(session_id)
	
		if wk is None:
			wk = self.create_session_wk(session_id)
	
		wk.append_row(record)


manager = GoogleSheetManager(gs, wk_s, wk_f)


class GoogleDataRetrieval:
	def __init__(self, manager):
		self.manager = manager

	@handle_exceptions
	def get_ethnicity_by_session_id(self, session_id):
		worksheet = self.manager.get_wk_by_name('sessions')
		session_id = str(session_id)
		matching_cells = worksheet.findall(session_id)
		cell = matching_cells[0]
		row = worksheet.row_values(cell.row)
		ethnicity = row[1]
		return ethnicity

	@handle_exceptions
	def get_rt_data_for_session(self, session_id):
		wk = manager.get_wk_by_name(session_id)

		if wk is None:
			return pd.DataFrame(columns=['session_id', 'ethnicity',
				'reaction_t', 'timeStamp'])

		records = wk.get_all_records()
		if records:
			return pd.DataFrame(records)
		else:
			return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t',
				'timeStamp'])
		

data_manager = GoogleDataRetrieval(manager)
