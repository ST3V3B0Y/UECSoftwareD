# Tabla "Software" que almacena la información de los software/programas que se usan en la sala 

from app import db

class Software(db.Model):
    __tablename__ = 'software'
    idSoftware = db.Column(db.Integer, primary_key=True, nullable=False)
    nombreSoftware =  db.Column(db.String(100), nullable=False)
    historiales = db.relationship('Historial', backref='software', lazy=True)

