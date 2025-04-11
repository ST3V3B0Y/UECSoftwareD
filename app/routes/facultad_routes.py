# Importaciones de Flask y extensiones relacionadas
from flask import Blueprint, render_template, flash, request, redirect, url_for
# Blueprint: Para crear módulos de rutas
# render_template: Para renderizar plantillas HTML
# flash: Para mostrar mensajes flash al usuario
# request: Para manejar solicitudes HTTP
# redirect, url_for: Para redireccionar a otras rutas

from app import db  # Importa la instancia de la base de datos SQLAlchemy

# Crea un Blueprint llamado 'facultad' para agrupar rutas relacionadas
bp = Blueprint("facultad", __name__)

# Ruta principal para la facultad
@bp.route("/facultad")
def indexFacultad():
    """
    Maneja la ruta principal de facultad.
    Simplemente renderiza la plantilla index.html ubicada en administracion/facultad/
    """
    return render_template('administracion/facultad/index.html')