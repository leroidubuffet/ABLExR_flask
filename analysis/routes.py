from flask import Blueprint, render_template, request, redirect, url_for

from constants import INSERT_FOUR_DIGIT_NUMBER, SESSION_ID_NOT_EXIST
from utils import validate_session_id
from google_sheets import manager
from chart import chart_render_seaborn_chart

analyze_routes = Blueprint('analysis', __name__)


@analyze_routes.route('/analyze_session', methods=['GET', 'POST'])
def analyze_session():
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
                return redirect(url_for('trainer.analysis_chart', 
                                        session_id=session_id))        

    return render_template('analyze_session.html', error=error)


@analyze_routes.route('/analysis/<session_id>', methods=['GET', 'POST'])
def analysis_chart(session_id):
    if request.method == 'POST':
        dimension = request.form.get('dimension')
    else:
        dimension = 'Anger'
    return chart_render_seaborn_chart(session_id, dimension=dimension)