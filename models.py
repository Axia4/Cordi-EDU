from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class Roles(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.String(1024))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
        }

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer)
    # List of roles assigned to the user
    roles = db.relationship('Roles', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    default_aula = db.Column(db.String(36), db.ForeignKey('aulas.uuid'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'active': self.active,
            'last_login_at': self.last_login_at,
            'roles': [role.to_dict() for role in self.roles],
            'default_aula': self.default_aula,
        }
    def get_roles(self):
        return [role.name for role in self.roles]
    def get_permissions(self):
        perms = set()
        for role in self.roles:
            if role.permissions:
                perms.update(role.permissions.split(','))
        return list(perms)
class Centro(db.Model):
    __tablename__ = 'centros'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(512))
    telefono = db.Column(db.String(128))
    email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.uuid,
            'nombre': self.nombre,
            'direccion': self.direccion or '',
            'telefono': self.telefono or '',
            'email': self.email or '',
        }

class Aula(db.Model):
    __tablename__ = 'aulas'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    centro_id = db.Column(db.String(36), db.ForeignKey('centros.uuid'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    centro = db.relationship('Centro', backref=db.backref('aulas', lazy=True))

    def to_dict(self):
        return {
            'id': self.uuid,
            'nombre': self.nombre,
            'centro_id': self.centro_id,
        }
activity_aulas = db.Table('actividad_aulas',
    db.Column('actividad_id', db.Integer, db.ForeignKey('actividades.id'), primary_key=True),
    db.Column('aula_id', db.Integer, db.ForeignKey('aulas.id'), primary_key=True),
    # Estado (aceptado, rechazado, pendiente, quizá)
    db.Column('estado', db.String(20), default='pendiente'),
    # Notas (opcional)
    db.Column('notas', db.Text, nullable=True)
)
class Actividad(db.Model):
    __tablename__ = 'actividades'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fecha_hora_inicio = db.Column(db.DateTime, nullable=False)
    fecha_hora_fin = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.Text)
    aulas = db.relationship('Aula', secondary='actividad_aulas', backref=db.backref('actividades', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.uuid,
            'nombre': self.nombre,
            'fecha_hora_inicio': self.fecha_hora_inicio.isoformat(),
            'fecha_hora_fin': self.fecha_hora_fin.isoformat(),
            'descripcion': self.descripcion or '',
            'aulas': [aula.uuid for aula in self.aulas],
        }