# Tabla "Historial" en donde se encuentra la información de los equipos una vez son liberados, aquí se encontrará la hora de inicio y salida del usuario, fecha, sala, número de equipo, programa usado y usuario.

from app import db
from datetime import datetime

class Historial(db.Model):
    __tablename__ = 'historial'
    idHistorial = db.Column(db.Integer, primary_key=True)
    Usuario_idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario', ondelete='cascade'), nullable=False)
    fecha = db.Column(db.Date, default=datetime.now().date(), nullable=False)
    horaInicio = db.Column(db.Time, nullable=False)
    horaFin = db.Column(db.Time, nullable=True)
    Equipo_idEquipo = db.Column(db.Integer, db.ForeignKey('equipo.idEquipo', ondelete='cascade'), nullable=False)
    nombreSala = db.Column(db.String(10), nullable=False)
    software_idSoftware = db.Column(db.Integer, db.ForeignKey('software.idSoftware', ondelete='cascade'), nullable=False)
    otroSoftware = db.Column(db.String(265), nullable=True)