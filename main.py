from flask import Flask, render_template, request, g, redirect, url_for, session, flash
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from helpers import DATA_DIR
from models import db, User, Roles
import os
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-for-dev')

# Flask-Security configuration
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt-for-dev')
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_RESET_EMAIL'] = False


# Ensure DATA_DIR exists and create sqlite file path
DATA_DIR.mkdir(parents=True, exist_ok=True)
db_path = DATA_DIR / 'db.sqlite3'
# Use absolute path for SQLite on Windows
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.absolute().as_posix()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init extensions
# print("Using database at:", app.config['SQLALCHEMY_DATABASE_URI'])
db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Roles)
security = Security(app, user_datastore)

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
@login_required
def index():
    return render_template('index.html')


# --- blueprints -------------------------------------------------------------
from centros import centros
from aulas import aulas
app.register_blueprint(centros)
app.register_blueprint(aulas)

@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'user_datastore': user_datastore}

def create_default_data():
    """Create default users and roles if they don't exist"""
    import uuid
    from flask_security.utils import hash_password
    
    # Create roles if they don't exist
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin', description='Administrator')
    if not user_datastore.find_role('user'):
        user_datastore.create_role(name='user', description='Regular User')
    
    # Create admin user if it doesn't exist
    if not user_datastore.find_user(email='admin@example.com'):
        user_datastore.create_user(
            email='admin@example.com',
            password=hash_password('admin'),
            name='Administrator',
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            roles=['admin']
        )
    
    # Commit changes
    db.session.commit()

if __name__ == '__main__':
    # create DB file and tables if missing (useful for dev without running migrations)
    with app.app_context():
        db.create_all()
        create_default_data()
    app.run(host='0.0.0.0', port=3129, debug=True)
