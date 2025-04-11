from app import db  # Importa la instancia de SQLAlchemy para la conexión con la base de datos
from datetime import datetime  # Para manejar fechas y horas

class Historial(db.Model):
    """
    Modelo que representa el historial de uso de equipos y software por usuarios.
    Registra sesiones de trabajo en el sistema con sus detalles temporales.
    """
    __tablename__ = 'historial'  # Nombre de la tabla en la base de datos

    # CLAVE PRIMARIA
    idHistorial = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # RELACIÓN CON USUARIO (clave foránea)
    Usuario_idUsuario = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.idUsuario', on_delete='cascade'),  # Eliminación en cascada
        nullable=False
    )

    # FECHA Y HORAS DE LA SESIÓN
    fecha = db.Column(
        db.Date, 
        default=datetime.now().date(),  # Fecha actual por defecto
        nullable=False
    )
    horaInicio = db.Column(db.Time, nullable=False)  # Hora de inicio (obligatoria)
    horaFin = db.Column(db.Time, nullable=True)      # Hora de fin (opcional para sesiones activas)

    # RELACIÓN CON EQUIPO (clave foránea)
    Equipo_idEquipo = db.Column(
        db.Integer,
        db.ForeignKey('equipo.idEquipo', on_delete='cascade'),  # Eliminación en cascada
        nullable=False
    )

    # DATOS DE UBICACIÓN
    nombreSala = db.Column(db.String(10), nullable=False)  # Nombre de sala (10 caracteres máx)

    # RELACIÓN CON SOFTWARE (clave foránea)
    software_idSoftware = db.Column(
        db.Integer,
        db.ForeignKey('software.idSoftware', on_delete='cascade'),  # Eliminación en cascada
        nullable=False
    )

    # CAMPO PARA SOFTWARE NO CATALOGADO
    otroSoftware = db.Column(db.String(265), nullable=True)  # Software adicional (opcional)

    def __repr__(self):
        """Representación textual para depuración"""
        return (f'<Historial {self.idHistorial}: Usuario {self.Usuario_idUsuario} '
                f'en equipo {self.Equipo_idEquipo} ({self.fecha})>')