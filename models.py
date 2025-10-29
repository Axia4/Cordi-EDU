from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.String(1024))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'permissions': self.permissions,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_active = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)
    # List of roles assigned to the user
    roles = db.relationship('Roles', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    default_aula = db.Column(db.String(36), db.ForeignKey('aulas.uuid'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_active': self.is_active,
            'last_login': self.last_login,
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