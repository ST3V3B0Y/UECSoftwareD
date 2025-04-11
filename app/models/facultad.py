# Importa la instancia de SQLAlchemy (db) para la interacción con la base de datos
from app import db

class Facultad(db.Model):
    """
    Modelo que representa una facultad en el sistema.
    Mapea a la tabla 'facultad' en la base de datos.
    """
    __tablename__ = 'facultad'  # Nombre de la tabla en la base de datos

    # Atributos/Columnas:
    idFacultad = db.Column(db.Integer, primary_key=True)  # Clave primaria autoincremental
    nombreFacultad = db.Column(db.String(256), nullable=False)  # Nombre de la facultad (obligatorio)

    # Relación uno-a-muchos con Usuario:
    usuarios = db.relationship(
        'Usuario',  # Modelo relacionado
        backref='facultad',  # Crea referencia inversa en Usuario
        lazy=True,  # Carga perezosa (no carga usuarios hasta que se accede)
        cascade='all, delete, delete-orphan'  # Elimina usuarios relacionados al borrar facultad
    )

    def __repr__(self):
        """Representación legible del objeto para debugging"""
        return f'<Facultad {self.idFacultad}: {self.nombreFacultad}>'