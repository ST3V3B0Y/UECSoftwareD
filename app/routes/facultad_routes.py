# Importación de librerías necesarias
# flask: Framework para manejar rutas y vistas.
# db: La instancia de la base de datos de la aplicación.

from flask import Blueprint, render_template, flash, request, redirect, url_for
from app import db

# Definición del Blueprint para manejar las rutas relacionadas con la facultad.
bp = Blueprint("facultad", __name__)

# Ruta para mostrar la página principal de la facultad
@bp.route("/facultad")
def indexFacultad():
    # Renderiza la plantilla 'index.html' que se encuentra en la carpeta 'administracion/facultad'.
    return render_template('administracion/facultad/index.html')
