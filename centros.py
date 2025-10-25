from helpers import DATA_DIR, list_items, read_json_file, save_json_file, create_directory
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
centros = Blueprint('centros', __name__, url_prefix='/centros')

class CentroForm(FlaskForm):
    nombre = StringField('Nombre del Centro', validators=[DataRequired()])
    direccion = StringField('Dirección (opcional)')
    telefono = StringField('Teléfono (principal, opcional)')
    email = StringField('Correo electrónico (principal, opcional)')

@centros.route('/')
def index():
    centros = list_items('Centros')
    return render_template('centros/index.html', centros=centros)

@centros.route('/<centro_id>')
def detalle(centro_id):
    centro_data = DATA_DIR / 'Centros' / centro_id / '_data.json'
    centro_info = read_json_file(centro_data)
    return render_template('centros/detalle.html', centro=centro_info, centro_id=centro_id)

@centros.route('/select/<centro_id>')
def select(centro_id):
    centro_data = DATA_DIR / 'Centros' / centro_id / '_data.json'
    centro_info = read_json_file(centro_data)
    if centro_info:
        session['CentroActual'] = centro_id
        session['CentroActualName'] = centro_id
    return redirect(url_for('index'))

@centros.route('/new', methods=['GET', 'POST'])
def nuevo():
    form = CentroForm()
    if form.validate_on_submit():
        nuevo_centro = {
            'Nombre': form.nombre.data,
            'Dirección': form.direccion.data,
            'Teléfono': {"Principal": form.telefono.data} if form.telefono.data else {},
            'Correo electrónico': {"Principal": form.email.data} if form.email.data else {}
        }
        # Crear carpeta y guardar datos en _data.json
        centro_id = str(uuid.uuid4())
        centro_dir = DATA_DIR / 'Centros' / centro_id
        create_directory(centro_dir)
        save_json_file(centro_dir / '_data.json', nuevo_centro)
        return redirect(url_for('centros.index'))
    return render_template('centros/nuevo.html', form=form)