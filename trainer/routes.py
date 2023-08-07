from flask import Blueprint, render_template, request, redirect, url_for

from config import PASSWORD
from constants import INVALID_PASSWORD, ETHNICITIES, SESSION_ID_EXISTS,\
      SESSION_ID_MUST_BE_DIGIT
from utils import get_race_digit
from google_sheets import manager


trainer_routes = Blueprint('trainer', __name__)


def create_new_session(user_session_id, race_digit, session_description):
    if user_session_id and user_session_id.isdigit() and \
            len(user_session_id) <= 3 and \
            race_digit is not None:
        session_id = race_digit + user_session_id.zfill(3)
        if manager.get_wk_by_name(session_id):
            return session_id, SESSION_ID_EXISTS
        else:
            manager.add_session(session_id, session_description)
            manager.create_session_wk(session_id)
            return session_id, None
    return None, SESSION_ID_MUST_BE_DIGIT


@trainer_routes.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':  # DELETE
        if request.form['password'] != PASSWORD:
            error = INVALID_PASSWORD
        else:
            return redirect(url_for('trainer.trainer_dashboard'))
    return render_template('login.html', error=error)


@trainer_routes.route('/trainer_dashboard')
def trainer_dashboard():
    return render_template('trainer_dashboard.html')


@trainer_routes.route('/new_session', methods=['GET', 'POST'])
def new_session():
    ethnicities = ETHNICITIES
    session_id = None
    form_submitted = False
    error = None

    if request.method == 'POST':
        form_submitted = True
        ethnicity = request.form['ethnicity']
        race_digit = get_race_digit(ethnicity)
        user_session_id = request.form['session_id']
        session_description = request.form['session_description']
        session_id, error = create_new_session(user_session_id, race_digit, 
                                               session_description)
    return render_template('new_session.html', ethnicities=ethnicities, 
                           session_id=session_id, 
                           form_submitted=form_submitted,
                           error=error)


# @trainer_routes.route('/analyze_session', methods=['GET', 'POST'])
# def analyze_session():
#     session_id = None
#     form_submitted = False
#     error = None

#     if request.method == 'POST':
#         form_submitted = True
#         session_id = request.form['session_id']

#         return redirect((url_for('analysis.render_seaborn_chart', 
#                                 session_id=session_id)))

#     return render_template('analyze_session.html', error=error)


# @trainer_routes.route('/analyze_session', methods=['GET', 'POST'])
# def analyze_session():
#     error = None
#     if request.method == 'POST':
#         session_id = request.form['session_id']

#         if not validate_session_id(session_id):
#             error = INSERT_FOUR_DIGIT_NUMBER
#         else:
#             session_exists = get_wk_by_name(session_id)

#             if not session_exists:
#                 error = SESSION_ID_NOT_EXIST
#             else:
#                 return redirect(url_for('render_seaborn_chart', session_id=session_id))        

#     return render_template('analyze_session.html', error=error)