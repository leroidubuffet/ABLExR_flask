from flask import Blueprint, render_template, request, redirect, url_for,\
    session

from constants import INSERT_FOUR_DIGIT_NUMBER, SESSION_ID_NOT_EXIST
from utils import validate_session_id
from google_sheets import manager

trainee_routes = Blueprint('trainee', __name__)


@trainee_routes.route('/experience_menu')
def experience_menu():
    return render_template('experience_menu.html')


@trainee_routes.route('/video_login', methods=['GET', 'POST'])
def video_login():
    error = None
    if request.method == 'POST':
        session_id = request.form['session_id']

        if not validate_session_id(session_id):
            error = INSERT_FOUR_DIGIT_NUMBER
        else:
            session_exists = manager.get_wk_by_name(session_id)

            if not session_exists:
                error = SESSION_ID_NOT_EXIST
            else:
                session['session_id'] = session_id
                return redirect(url_for('trainee.waiting_room', session_id=session_id))

    return render_template('video_login.html', error=error)


@trainee_routes.route('/waiting_room/<session_id>')
def waiting_room(session_id):
    return render_template('waiting_room.html', session_id=session_id)


@trainee_routes.route('/ar_vr')
def ar_vr():
    return render_template('ar_vr.html')


@trainee_routes.route('/video')
def video():
    session_id = request.args.get('session_id')
    return render_template('video.html', session_id=session_id)


@trainee_routes.route('/save_responsetime', methods=['POST'])
def save_responsetime():
    data = request.get_json()
    session_id = session.get('session_id')
    response_time = round(float(data['timestamp']), 2)
    response_time = str(response_time).replace(',', '.')

    try:
        manager.add_record(session_id, response_time)
        return 'Time saved', 200
    except ValueError as ve:
        trainee_routes.logger.error('Error when saving response time: %s', ve)
        return str(ve), 400
    except Exception as e:
        trainee_routes.logger.error('Error when saving response time: %s', e)
        return 'Internal server error', 500


@trainee_routes.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback = request.form['feedback']
        session_id = session.get('session_id')

        try:
            manager.add_feedback(session_id, feedback)

            return render_template('feedback.html',
                                   message='Thank you for your feedback.',
                                   form_submitted=True), 200
        except ValueError as ve:
            trainee_routes.logger.error('Error when saving feedback: %s', ve)
            return str(ve), 400
        except Exception as e:
            return render_template('feedback.html', 
                                   message='Unable \
                                   to save your feedback.'), 500
    else:
        return render_template('feedback.html')
