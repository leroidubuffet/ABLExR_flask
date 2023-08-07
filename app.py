from flask import Flask, render_template
from trainer.routes import trainer_routes
from trainee.routes import trainee_routes
from analysis.routes import analyze_routes
from config import SECRET_KEY


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    app.secret_key = SECRET_KEY

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(trainer_routes, url_prefix='/trainer')
    app.register_blueprint(trainee_routes, url_prefix='/trainee')
    app.register_blueprint(analyze_routes, url_prefix='/analysis')


app = create_app()


@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run()