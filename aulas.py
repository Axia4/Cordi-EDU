from helpers import DATA_DIR
import uuid
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, g, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from models import Aula, Centro, db

aulas = Blueprint('aulas', __name__, url_prefix='/aulas')


class AulaForm(FlaskForm):
    nombre = StringField('Nombre del Aula', validators=[DataRequired()])
    centro_id = SelectField('Centro', validators=[DataRequired()], coerce=str)

    def __init__(self, *args, **kwargs):
        super(AulaForm, self).__init__(*args, **kwargs)
        # Populate centro choices with empty option first
        centros_list = Centro.query.order_by(Centro.nombre.asc()).all()
        self.centro_id.choices = [('', 'Seleccionar centro...')] + [(centro.uuid, centro.nombre) for centro in centros_list]

@aulas.route('/')
def index():
    # list all aulas from DB grouped by centro
    aulas_q = Aula.query.join(Centro).order_by(Centro.nombre.asc(), Aula.nombre.asc()).all()
    
    # Group aulas by centro
    aulas_by_centro = {}
    for aula in aulas_q:
        centro_nombre = aula.centro.nombre
        if centro_nombre not in aulas_by_centro:
            aulas_by_centro[centro_nombre] = {
                'centro': aula.centro,
                'aulas': []
            }
        aulas_by_centro[centro_nombre]['aulas'].append(aula)
    
    print("Aulas found:", aulas_q)
    return render_template('aulas/index.html', aulas_by_centro=aulas_by_centro)

@aulas.route('/<aula_id>')
def detalle(aula_id):
    aula = Aula.query.filter_by(uuid=aula_id).first()
    if not aula:
        return redirect(url_for('aulas.index'))
    return render_template('aulas/detalle.html', aula=aula.to_dict(), aula_id=aula.uuid, centro=aula.centro)

@aulas.route('/<aula_id>/select')
def select(aula_id):
    next_redirect = request.args.get('next', url_for('index'))
    aula = Aula.query.filter_by(uuid=aula_id).first()
    if aula:
        session['AulaActual'] = aula.uuid
        session['AulaActualName'] = aula.nombre
    return redirect(next_redirect)

@aulas.route('/choose')
def choose():
    aulas_q = Aula.query.join(Centro).order_by(Aula.nombre.asc()).all()
    return render_template('aulas/choose.html', aulas=aulas_q)

@aulas.route('/<aula_id>/edit', methods=['GET', 'POST'])
def editar(aula_id):
    aula = Aula.query.filter_by(uuid=aula_id).first()
    if not aula:
        flash('Aula no encontrada.', 'warning')
        return redirect(url_for('aulas.index'))
    form = AulaForm(obj=aula)
    if form.validate_on_submit():
        aula.nombre = form.nombre.data
        aula.centro_id = form.centro_id.data
        db.session.commit()
        return redirect(url_for('aulas.detalle', aula_id=aula.uuid))
    return render_template('aulas/editar.html', form=form, aula_id=aula.uuid)

@aulas.route('/new', methods=['GET', 'POST'])
def nuevo():
    form = AulaForm()
    if form.validate_on_submit():
        aula_id = str(uuid.uuid4())
        nuevo = Aula(uuid=aula_id, nombre=form.nombre.data, centro_id=form.centro_id.data)
        db.session.add(nuevo)
        db.session.commit()
        flash('Aula creada correctamente.', 'success')
        return redirect(url_for('aulas.index'))
    return render_template('aulas/nuevo.html', form=form)

@aulas.route('/<aula_id>/delete', methods=['GET', 'POST'])
def borrar(aula_id):
    if request.method == 'GET':
        aula = Aula.query.filter_by(uuid=aula_id).first()
        if not aula:
            flash('Aula no encontrada.', 'warning')
            return redirect(url_for('aulas.index'))
        return render_template('aulas/borrar.html', aula_id=aula_id, aula=aula.to_dict(), centro=aula.centro)
    aula = Aula.query.filter_by(uuid=aula_id).first()
    if not aula:
        flash('Aula no encontrada.', 'danger')
        return redirect(url_for('aulas.index'))
    db.session.delete(aula)
    db.session.commit()
    flash('Aula eliminada correctamente.', 'success')
    return redirect(url_for('aulas.index'))
