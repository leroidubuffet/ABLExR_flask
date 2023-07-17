import gspread
from utils import map_ethnicity
import pandas as pd
import gspread
from datetime import datetime


# Google Sheets setup
gc = gspread.service_account_from_dict(credentials)
gs = gc.open("ABLExR-DATA")		# open document
wk_rt = gs.get_worksheet(0) 	# reaction time spreadsheet
wk_s = gs.worksheet('sessions')	# session spreadsheet
wk_f = gs.worksheet('feedback') # feedback spreadsheet

def get_last_added_wk(gs):
	worksheets = gs.worksheets()    
	if worksheets:
		return worksheets[-1]
	else:
		return None
	
def get_ethnicity_by_session_id(session_id):
    worksheet = get_wk_by_name('sessions')

    if worksheet is None:
        return 'Sheet not found'

    records = worksheet.get_all_records()
    df = pd.DataFrame.from_records(records)
    session_id = int(session_id)
    session_data = df[df['session_id'] == session_id]

    if session_data.empty:
        return 'Session not found'

    return session_data['ethnicity'].iloc[0]

def get_wk_by_name(session_id):
	try:
		worksheet = gs.worksheet(session_id)
		return gs.worksheet(session_id)
	except gspread.exceptions.WorksheetNotFound:
		return None
	
def create_session_wk(id):
	wk = gs.add_worksheet(str(id), 0, 3)
	wk.append_row(["ethnicity", "reaction_t", "timeStamp"])
	return wk

def delete_wk(name):
	wk = get_wk_by_name(name)
	if wk is not None:
		gs.del_worksheet(wk)

def get_rt_data_for_session(session_id):
    wk = get_wk_by_name(session_id)
    
    if wk is None:
        return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t', 'timeStamp'])
    
    records = wk.get_all_records()
    if records:
        return pd.DataFrame(records)
    else:
        return pd.DataFrame(columns=['session_id', 'ethnicity', 'reaction_t', 'timeStamp'])

def get_rt_data(session_id):
    print(f"Getting data for session_id: {session_id}")
    wk = gs.worksheet(session_id)
    records = wk.get_all_records()
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

df_s = get_s_data()
df_f = get_f_data()

def add_record(session_id, reaction_t):
	session_id = str(session_id)
	ethnicity_code = int(session_id[0])
	ethnicity = map_ethnicity(ethnicity_code)
	now = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
	record = [ethnicity, reaction_t, now]
	
	wk = get_wk_by_name(session_id)
	
	if wk is None:
		wk = create_session_wk(session_id)
	
	wk.append_row(record)

def add_session(session_id, session_description):
	ethnicity_code = int(session_id[0])
	ethnicity = map_ethnicity(ethnicity_code)
	record = [session_id, ethnicity, session_description]
	wk_s.append_row(record, value_input_option='USER_ENTERED')

def add_feedback(session_id, feedback):
	try:
		session_id = str(session_id)
		ethnicity_code = int(session_id[0])
		ethnicity = map_ethnicity(ethnicity_code)
		record = [session_id, ethnicity, feedback]
		wk_f.append_row(record, value_input_option='USER_ENTERED')
	except Exception as e:
		app.logger.error('Error when adding feedback: %s', e)
