from app import db  # Importa la instancia de SQLAlchemy para la conexión con la base de datos

class Software(db.Model):
    """
    Modelo que representa una aplicación de software en el sistema.
    
    Atributos:
        idSoftware (int): Identificador único del software (clave primaria)
        nombreSoftware (str): Nombre de la aplicación (máx. 100 caracteres)
        historiales (relationship): Relación con los registros de uso del software
    
    Relaciones:
        - Tiene una relación uno-a-muchos con el modelo Historial
    """
    __tablename__ = 'software'  # Nombre de la tabla en la base de datos

    # Identificador único del software
    idSoftware = db.Column(
        db.Integer, 
        primary_key=True,  # Clave primaria
        nullable=False,    # No puede ser nulo
        autoincrement=True # Auto-incremental
    )

    # Nombre de la aplicación
    nombreSoftware = db.Column(
        db.String(100),    # Tipo string con máximo 100 caracteres
        nullable=False     # Campo obligatorio
    )

    # Relación con los registros de uso (historial)
    historiales = db.relationship(
        'Historial',                # Modelo relacionado (Historial)
        backref='software',         # Crea atributo 'software' en Historial
        lazy='dynamic',             # Carga dinámica para mejor performance
        cascade='all, delete-orphan', # Elimina registros hijos al borrar
        order_by='desc(Historial.fecha)'  # Ordena historial por fecha descendente
    )

    def __repr__(self):
        """
        Representación oficial del objeto Software.
        
        Returns:
            str: Representación en string del objeto
        """
        return f'<Software [ID: {self.idSoftware}] - {self.nombreSoftware}>'

    def to_dict(self):
        """
        Convierte el objeto Software a un diccionario.
        
        Returns:
            dict: Diccionario con los atributos del software
        """
        return {
            'id': self.idSoftware,
            'nombre': self.nombreSoftware,
            'total_usos': len(self.historiales.all())
        }