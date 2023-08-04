from flask import Flask, render_template
from trainer.routes import trainer_routes
from trainee.routes import trainee_routes
from analysis.routes import analyze_routes
from config import SECRET_KEY

app = Flask(__name__)
app.config['DEBUG'] = True  # Explicitly set debug mode

app.secret_key = SECRET_KEY

# Register the blueprints
app.register_blueprint(trainer_routes, url_prefix='/trainer')
app.register_blueprint(trainee_routes, url_prefix='/trainee')
app.register_blueprint(analyze_routes, url_prefix='/analysis')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
