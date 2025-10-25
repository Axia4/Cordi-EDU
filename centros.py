from helpers import DATA_DIR
import uuid
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, g, current_app
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from models import Centro, db

centros = Blueprint('centros', __name__, url_prefix='/centros')

class CentroForm(FlaskForm):
    nombre = StringField('Nombre del Centro', validators=[DataRequired()])
    direccion = StringField('Dirección (opcional)')
    telefono = StringField('Teléfono (principal, opcional)')
    email = StringField('Correo electrónico (principal, opcional)')

@centros.route('/')
def index():
    # list all centros from DB
    centros_q = Centro.query.order_by(Centro.nombre.asc()).all()
    print("Centros found:", centros_q)
    return render_template('centros/index.html', centros=centros_q)

@centros.route('/<centro_id>')
def detalle(centro_id):
    centro = Centro.query.filter_by(uuid=centro_id).first()
    if not centro:
        return redirect(url_for('centros.index'))
    return render_template('centros/detalle.html', centro=centro.to_dict(), centro_id=centro.uuid)

@centros.route('/<centro_id>/select')
def select(centro_id):
    next_redirect = request.args.get('next', url_for('index'))
    centro = Centro.query.filter_by(uuid=centro_id).first()
    if centro:
        session['CentroActual'] = centro.uuid
        session['CentroActualName'] = centro.nombre
    return redirect(next_redirect)

@centros.route('/choose')
def choose():
    centros_q = Centro.query.order_by(Centro.nombre.asc()).all()
    return render_template('centros/choose.html', centros=centros_q)

@centros.route('/<centro_id>/edit', methods=['GET', 'POST'])
def editar(centro_id):
    centro = Centro.query.filter_by(uuid=centro_id).first()
    if not centro:
        flash('Centro no encontrado.', 'warning')
        return redirect(url_for('centros.index'))
    form = CentroForm(obj=centro)
    if form.validate_on_submit():
        centro.nombre = form.nombre.data
        centro.direccion = form.direccion.data or ''
        centro.telefono = form.telefono.data or ''
        centro.email = form.email.data or ''
        db.session.commit()
        return redirect(url_for('centros.detalle', centro_id=centro.uuid))
    return render_template('centros/editar.html', form=form, centro_id=centro.uuid)

@centros.route('/new', methods=['GET', 'POST'])
def nuevo():
    form = CentroForm()
    if form.validate_on_submit():
        centro_id = str(uuid.uuid4())
        telefono = form.telefono.data or ''
        email = form.email.data or ''
        nuevo = Centro(uuid=centro_id, nombre=form.nombre.data, direccion=form.direccion.data or '', telefono=telefono, email=email)
        db.session.add(nuevo)
        db.session.commit()
        flash('Centro creado correctamente.', 'success')
        return redirect(url_for('centros.index'))
    return render_template('centros/nuevo.html', form=form)

@centros.route('/<centro_id>/delete', methods=['GET', 'POST'])
def borrar(centro_id):
    if request.method == 'GET':
        centro = Centro.query.filter_by(uuid=centro_id).first()
        if not centro:
            flash('Centro no encontrado.', 'warning')
            return redirect(url_for('centros.index'))
        return render_template('centros/borrar.html', centro_id=centro_id, centro=centro.to_dict())
    centro = Centro.query.filter_by(uuid=centro_id).first()
    if not centro:
        flash('Centro no encontrado.', 'danger')
        return redirect(url_for('centros.index'))
    db.session.delete(centro)
    db.session.commit()
    flash('Centro eliminado correctamente.', 'success')
    return redirect(url_for('centros.index'))