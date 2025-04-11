from app import db  # Importa la instancia de SQLAlchemy para la conexión con la BD

class Software(db.Model):
    """
    Modelo que representa un programa de software en el sistema.
    Almacena información sobre aplicaciones disponibles y su uso registrado.
    """
    __tablename__ = 'software'  # Nombre de la tabla en la base de datos

    # Columna ID (clave primaria, autoincremental)
    idSoftware = db.Column(db.Integer, primary_key=True, nullable=False)

    # Nombre del software (campo obligatorio, máximo 100 caracteres)
    nombreSoftware = db.Column(db.String(100), nullable=False)

    # Relación uno-a-muchos con Historial (Registros de uso)
    historiales = db.relationship(
        'Historial',                # Modelo relacionado
        backref='software',         # Crea referencia inversa en Historial
        lazy=True,                  # Carga perezosa (no carga hasta que se accede)
        cascade='all, delete, delete-orphan'  # Reglas de eliminación automática
    )

    def __repr__(self):
        """Representación textual para depuración y registros"""
        return f'<Software {self.idSoftware}: {self.nombreSoftware}>'