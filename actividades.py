from helpers import DATA_DIR
import uuid
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, g, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget
from models import Actividad, Aula, db
from datetime import datetime

actividades = Blueprint('actividades', __name__, url_prefix='/actividades')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ActividadForm(FlaskForm):
    nombre = StringField('Nombre de la Actividad', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción (opcional)')
    fecha_hora_inicio = DateTimeLocalField('Fecha y Hora de Inicio', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    fecha_hora_fin = DateTimeLocalField('Fecha y Hora de Fin', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    aulas = MultiCheckboxField('Aulas', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(ActividadForm, self).__init__(*args, **kwargs)
        # Populate aulas choices grouped by centro
        from sqlalchemy.orm import joinedload
        aulas = Aula.query.options(joinedload(Aula.centro)).order_by(Aula.centro_id, Aula.nombre).all()
        self.aulas.choices = [(aula.id, f"{aula.centro.nombre} - {aula.nombre}") for aula in aulas]
        
        # Create grouped data for template
        self.aulas_grouped = {}
        for aula in aulas:
            centro_name = aula.centro.nombre
            if centro_name not in self.aulas_grouped:
                self.aulas_grouped[centro_name] = []
            self.aulas_grouped[centro_name].append({
                'id': aula.id,
                'nombre': aula.nombre,
                'selected': False
            })

@actividades.route('/')
def index():
    from calendar import monthrange
    from datetime import datetime, timedelta
    
    # Get current month and year, or from query params
    now = datetime.now()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    
    # Calculate first and last day of the month
    first_day = datetime(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num, 23, 59, 59)
    
    # Get all activities for the month
    actividades_q = Actividad.query.filter(
        Actividad.fecha_hora_inicio >= first_day,
        Actividad.fecha_hora_inicio <= last_day
    ).order_by(Actividad.fecha_hora_inicio.asc()).all()
    
    # Group activities by date
    activities_by_date = {}
    for actividad in actividades_q:
        date_key = actividad.fecha_hora_inicio.date()
        if date_key not in activities_by_date:
            activities_by_date[date_key] = []
        activities_by_date[date_key].append(actividad)
    
    # Calculate calendar grid (including previous/next month days)
    start_weekday = first_day.weekday()  # 0 = Monday
    calendar_start = first_day - timedelta(days=start_weekday)
    
    # Generate 6 weeks (42 days) for complete calendar grid
    calendar_days = []
    current_date = calendar_start
    for week in range(6):
        week_days = []
        for day in range(7):
            day_activities = activities_by_date.get(current_date.date(), [])
            week_days.append({
                'date': current_date,
                'is_current_month': current_date.month == month,
                'is_today': current_date.date() == now.date(),
                'activities': day_activities
            })
            current_date += timedelta(days=1)
        calendar_days.append(week_days)
    
    # Navigation dates
    prev_month = first_day - timedelta(days=1)
    next_month = last_day + timedelta(days=1)
    
    return render_template('actividades/index.html', 
                         calendar_days=calendar_days,
                         current_month=first_day,
                         prev_month=prev_month,
                         next_month=next_month,
                         activities_by_date=activities_by_date)

@actividades.route('/<actividad_id>')
def detalle(actividad_id):
    actividad = Actividad.query.filter_by(uuid=actividad_id).first()
    if not actividad:
        return redirect(url_for('actividades.index'))
    return render_template('actividades/detalle.html', actividad=actividad.to_dict(), actividad_id=actividad.uuid, actividad_obj=actividad)

@actividades.route('/<actividad_id>/edit', methods=['GET', 'POST'])
def editar(actividad_id):
    actividad = Actividad.query.filter_by(uuid=actividad_id).first()
    if not actividad:
        flash('Actividad no encontrada.', 'warning')
        return redirect(url_for('actividades.index'))
    
    form = ActividadForm(obj=actividad)
    if request.method == 'GET':
        # Pre-populate the aulas field with current aulas
        form.aulas.data = [aula.id for aula in actividad.aulas]
        # Update the grouped data to show selected aulas
        selected_aula_ids = set(aula.id for aula in actividad.aulas)
        for centro_name in form.aulas_grouped:
            for aula in form.aulas_grouped[centro_name]:
                aula['selected'] = aula['id'] in selected_aula_ids
    
    if form.validate_on_submit():
        actividad.nombre = form.nombre.data
        actividad.descripcion = form.descripcion.data or ''
        actividad.fecha_hora_inicio = form.fecha_hora_inicio.data
        actividad.fecha_hora_fin = form.fecha_hora_fin.data
        
        # Update aulas relationship
        selected_aulas = Aula.query.filter(Aula.id.in_(form.aulas.data)).all()
        actividad.aulas = selected_aulas
        
        db.session.commit()
        flash('Actividad actualizada correctamente.', 'success')
        return redirect(url_for('actividades.detalle', actividad_id=actividad.uuid))
    return render_template('actividades/editar.html', form=form, actividad_id=actividad.uuid)

@actividades.route('/new', methods=['GET', 'POST'])
def nuevo():
    form = ActividadForm()
    
    # Pre-fill date if coming from calendar
    if request.method == 'GET' and 'date' in request.args:
        from datetime import datetime
        try:
            selected_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
            # Set default times: start at 9:00 AM, end at 10:00 AM
            form.fecha_hora_inicio.data = selected_date.replace(hour=9, minute=0)
            form.fecha_hora_fin.data = selected_date.replace(hour=10, minute=0)
        except ValueError:
            pass  # Invalid date format, ignore
    
    if form.validate_on_submit():
        actividad_id = str(uuid.uuid4())
        nueva_actividad = Actividad(
            uuid=actividad_id, 
            nombre=form.nombre.data, 
            descripcion=form.descripcion.data or '',
            fecha_hora_inicio=form.fecha_hora_inicio.data,
            fecha_hora_fin=form.fecha_hora_fin.data
        )
        
        # Add selected aulas
        selected_aulas = Aula.query.filter(Aula.id.in_(form.aulas.data)).all()
        nueva_actividad.aulas = selected_aulas
        
        db.session.add(nueva_actividad)
        db.session.commit()
        flash('Actividad creada correctamente.', 'success')
        return redirect(url_for('actividades.index'))
    return render_template('actividades/nuevo.html', form=form)

@actividades.route('/<actividad_id>/delete', methods=['GET', 'POST'])
def borrar(actividad_id):
    if request.method == 'GET':
        actividad = Actividad.query.filter_by(uuid=actividad_id).first()
        if not actividad:
            flash('Actividad no encontrada.', 'warning')
            return redirect(url_for('actividades.index'))
        return render_template('actividades/borrar.html', actividad_id=actividad_id, actividad=actividad.to_dict())
    
    actividad = Actividad.query.filter_by(uuid=actividad_id).first()
    if not actividad:
        flash('Actividad no encontrada.', 'danger')
        return redirect(url_for('actividades.index'))
    
    db.session.delete(actividad)
    db.session.commit()
    flash('Actividad eliminada correctamente.', 'success')
    return redirect(url_for('actividades.index'))
