from datetime import datetime
import logging

import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound, \
	CellNotFound, NoValidUrlKeyFound, APIError
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
gs = gc.open(DOCUMENT_NAME)		 # open document
wk_rt = gs.get_worksheet(0) 	 # reaction time worksheet
wk_s = gs.worksheet('sessions')	 # session worksheet
wk_f = gs.worksheet('feedback')  # feedback worksheet


class GoogleSheetManager:
	def __init__(self, gs, wk_s, wk_f):
		self.gs = gs
		self.wk_s = wk_s
		self.wk_f = wk_f

	def create_session_wk(self, session_id, rows=0, cols=3):
		try:
			wk = self.gs.add_worksheet(str(session_id), rows, cols)
			wk.append_row(["ethnicity", "reaction_t", "timeStamp"])
			return wk
		except Exception as e:
			logging.error('Error when creating session worksheet: %s', e)
			return None
	
	def add_session(self, session_id, session_description):
		try:
			ethnicity_code = int(session_id[0])
			ethnicity = map_ethnicity(ethnicity_code)
			record = [session_id, ethnicity, session_description]
			self.wk_s.append_row(record, value_input_option='USER_ENTERED')
		except WorksheetNotFound:
			logging.error(f"The specified worksheet for session '{session_id}' was not found.")
		except Exception as e:
			logging.error('Error when adding session: %s', e)

	def add_feedback(self, session_id, feedback):
		try:
			session_id = str(session_id)
			ethnicity_code = int(session_id[0])
			ethnicity = map_ethnicity(ethnicity_code)
			record = [session_id, ethnicity, feedback]
			self.wk_f.append_row(record, value_input_option='USER_ENTERED')
		except WorksheetNotFound:
			logging.error(f"The specified worksheet for session '{session_id}' was not found.")
		except Exception as e:
			logging.error('Error when adding feedback: %s', e)
	
	def add_record(self, session_id, reaction_t):
		try:
			session_id = str(session_id)
			ethnicity_code = int(session_id[0])
		except ValueError:
			logging.error("Error converting session ID")
			return
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
		record = [ethnicity, reaction_t, now]
	
		wk = data_manager.get_wk_by_name(session_id)
	
		if wk is None:
			wk = self.create_session_wk(session_id)
	
		wk.append_row(record)


manager = GoogleSheetManager(gs, wk_s, wk_f)


class GoogleDataRetrieval:
	def __init__(self, manager):
		self.manager = manager

	def get_wk_by_name(self, session_id):
		try:
			return self.manager.gs.worksheet(session_id)
		except WorksheetNotFound:
			logging.error(f"The specified worksheet for session '{session_id}' was not \
				found.")
		except Exception as e:
			logging.error('Error when getting worksheet: %s', e)

	def get_ethnicity_by_session_id(self, session_id):
		try:
			worksheet = self.get_wk_by_name('sessions')
		except WorksheetNotFound:
			logging.error(f"The specified worksheet for session '{session_id}' was not \
				found.")
		except Exception as e:
			logging.error('Error when getting worksheet: %s', e)

		session_id = str(session_id)

		matching_cells = worksheet.findall(session_id)

		if not matching_cells:
			return 'Session not found'

		cell = matching_cells[0]

		row = worksheet.row_values(cell.row)

		ethnicity = row[1]

		if not ethnicity:
			return 'Ethnicity not found'

		return ethnicity

	def get_rt_data_for_session(self, session_id):
		wk = self.get_wk_by_name(session_id)

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
