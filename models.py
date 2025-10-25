from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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