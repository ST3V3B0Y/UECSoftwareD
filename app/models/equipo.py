# Importa la instancia de SQLAlchemy (db) que maneja la conexión con la base de datos
# y proporciona los métodos para definir modelos
from app import db

class Equipo(db.Model):
    """
    Modelo que representa un equipo en la base de datos.
    Hereda de db.Model para tener funcionalidad ORM de SQLAlchemy.
    """
    __tablename__ = 'equipo'  # Nombre de la tabla en la base de datos

    # Columnas de la tabla:
    idEquipo = db.Column(db.Integer, primary_key=True)  # ID único (clave primaria)
    estadoEquipo = db.Column(db.String(256), nullable=False)  # Estado del equipo (requerido)
    sala = db.Column(db.String(5), nullable=False)  # Sala donde está ubicado (requerido)
    ipEquipo = db.Column(db.String(30), nullable=False)  # Dirección IP del equipo (requerido)

    def __repr__(self):
        """
        Representación string del objeto Equipo.
        Útil para debugging y mostrar información en consola.
        """
        return f'<Equipo: {self.estadoEquipo}>'  # Muestra el estado del equipo al imprimir el objeto