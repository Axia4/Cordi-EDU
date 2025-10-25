from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from helpers import DATA_DIR
from models import db
from flask_migrate import Migrate
import os
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-for-dev')

# Ensure DATA_DIR exists and create sqlite file path
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / 'db.sqlite3'
# Use absolute path for SQLite on Windows
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.absolute().as_posix()}"
print("Using database at:", app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init extensions
db.init_app(app)
migrate = Migrate(app, db)

@app.before_request
def before_request():
    g.NAV_ENDPOINT = request.endpoint
    g.CentroActual = session.get('CentroActual', '') != ''
    g.CentroActualName = session.get('CentroActualName', 'Ninguno')
    g.AulaActual = session.get('AulaActual', '') != ''
    g.AulaActualName = session.get('AulaActualName', 'Ninguna')
    # ensure cart exists in session
    session.setdefault('cart', [])


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
