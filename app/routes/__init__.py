# Rutas para acceder a la base de datos y realizar acciones CRUD (Create, Read, Update, Delete)

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.routes import accion_routes, equipo_routes, facultad_routes, historial_routes, usuario_routes,software_routes