from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from flask_login import LoginManager
from helpers import DATA_DIR
from models import db
import os
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-for-dev')

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# Ensure DATA_DIR exists and create sqlite file path
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / 'db.sqlite3'
# Use absolute path for SQLite on Windows
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.absolute().as_posix()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init extensions
# print("Using database at:", app.config['SQLALCHEMY_DATABASE_URI'])
db.init_app(app)

@app.before_request
def before_request():
    g.NAV_ENDPOINT = request.endpoint
    g.CentroActual = session.get('CentroActual', '') != ''
    g.CentroActualName = session.get('CentroActualName', 'Ninguno')
    g.AulaActual = session.get('AulaActual', '') != ''
    g.AulaActualName = session.get('AulaActualName', 'Ninguna')
    # ensure cart exists in session
    session.setdefault('cart', [])

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# --- routes ------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# --- blueprints -------------------------------------------------------------
from centros import centros
from aulas import aulas
app.register_blueprint(centros)
app.register_blueprint(aulas)

@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db}

if __name__ == '__main__':
    # create DB file and tables if missing (useful for dev without running migrations)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=3129, debug=True)
