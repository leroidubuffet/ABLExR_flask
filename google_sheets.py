from datetime import datetime
import logging

import gspread
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound, \
    CellNotFound, NoValidUrlKeyFound, APIError
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from constants import CREDENTIALS_FILE, DOCUMENT_NAME
from utils import reverse_map_ethnicity
from functools import wraps


# Configure logging
logging.basicConfig(level=logging.INFO)


# Exception handling decorator
def handle_exceptions(context=""):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SpreadsheetNotFound:
                logging.error(f"{context} Spreadsheet not found \
                for session_id: {args[1]}")
            except NoValidUrlKeyFound:
                logging.error(f"{context} No valid URL key found \
                for session_id: {args[1]}")
            except WorksheetNotFound:
                logging.error(f"{context} Worksheet not found \
                for session_id: {args[1]}")
            except CellNotFound:
                logging.error(f"{context} Cell not found \
                for session_id: {args[1]}")
            except APIError as e:
                logging.error(f"{context} API Error when working with \
                session_id: {args[1]}. Error: {str(e)}")
            except Exception as e:
                logging.error(f"{context} Error: {str(e)}")
            return None
        return wrapper
    return decorator


class GoogleSheetsManager:
    @staticmethod
    def authenticate(CREDENTIALS_FILE):
        """Authenticate using the provided credentials file"""
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file",
                 "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope)
        return gspread.authorize(creds)

    def __init__(self):
        self.gc = self.authenticate(CREDENTIALS_FILE)
        self.gs = self.gc.open(DOCUMENT_NAME)
        self.wk_rt = self.gs.get_worksheet(0)  		# reaction time worksheet
        self.wk_s = self.gs.worksheet('sessions')  	# session worksheet
        self.wk_f = self.gs.worksheet('feedback')  	# feedback worksheet

    def _get_or_create_worksheet(self, session_id: str):
        wk = self.get_wk_by_name(session_id)
        if wk is None:
            wk = self.create_session_wk(session_id)
        return wk

    def _get_ethnicity(self, session_id: str):
        session_id = str(session_id)
        ethnicity_code = session_id[0]
        return reverse_map_ethnicity(ethnicity_code)

    @handle_exceptions(context="Getting worksheet by name")
    def get_wk_by_name(self, session_id):
        return self.gs.worksheet(session_id)

    @handle_exceptions(context="Creating worksheet")
    def create_session_wk(self, session_id, rows=0, cols=3):
        wk = self.gs.add_worksheet(str(session_id), rows, cols)
        wk.append_row(["ethnicity", "reaction_t", "timeStamp"])
        return wk

    @handle_exceptions(context="Adding session")
    def add_session(self, session_id, session_description):
        ethnicity_code = session_id[0]
        ethnicity = reverse_map_ethnicity(ethnicity_code)
        record = [session_id, ethnicity, session_description]
        self.wk_s.append_row(record, value_input_option='USER_ENTERED')

    @handle_exceptions(context="Adding feedback")
    def add_feedback(self, session_id, feedback):
        session_id = str(session_id)
        ethnicity_code = session_id[0]
        ethnicity = reverse_map_ethnicity(ethnicity_code)
        record = [session_id, ethnicity, feedback]
        self.wk_f.append_row(record, value_input_option='USER_ENTERED')
    
    @handle_exceptions(context="Adding record")
    def add_record(self, session_id, reaction_t):
        ethnicity = self._get_ethnicity(session_id)
        now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
        record = [ethnicity, reaction_t, now]
    
        wk = self._get_or_create_worksheet(session_id)
        wk.append_row(record)


manager = GoogleSheetsManager()


class GoogleDataRetrieval:
    def __init__(self, manager):
        self.manager = manager

    @handle_exceptions(context="Getting ethnicity")
    def get_ethnicity_by_session_id(self, session_id):
        session_id = str(session_id)
        worksheet = self.manager.get_wk_by_name('sessions')
        matching_cells = worksheet.findall(session_id)
        cell = matching_cells[0]
        row = worksheet.row_values(cell.row)
        ethnicity = row[1]
        return ethnicity

    @handle_exceptions(context="Getting response time data")
    def get_rt_data_for_session(self, session_id):
        wk = self.manager._get_or_create_worksheet(session_id)

        if wk is None:
            return pd.DataFrame(columns=[
                'session_id',
                'ethnicity',
                'reaction_t',
                'timeStamp'])

        records = wk.get_all_records()
        if records:
            return pd.DataFrame(records)
        else:
            return pd.DataFrame(columns=[
                'session_id',
                'ethnicity',
                'reaction_t',
                'timeStamp'])


data_manager = GoogleDataRetrieval(manager)
