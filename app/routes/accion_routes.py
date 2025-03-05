# Importación de librerías necesarias
# flask: Framework para crear la aplicación web y manejar rutas.
# sqlalchemy: ORM para interactuar con la base de datos MySQL.
# flask_login: Proporciona funcionalidades de autenticación de usuarios.
# models: Contiene los modelos de datos, como el modelo 'Equipo'.
# sqlalchemy.exc: Manejo de excepciones de integridad de base de datos.

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Equipo
from flask_login import (
    login_required, login_manager, UserMixin, login_user, logout_user, current_user,
)
from sqlalchemy.exc import IntegrityError

# Definición de un Blueprint para la parte de "acciones" de la aplicación
bp = Blueprint("accion", __name__)

# Ruta protegida que solo puede ser accedida por usuarios autenticados
# Redirige al usuario a diferentes páginas dependiendo de la acción seleccionada
@login_required
@bp.route("/accion", methods=["GET", "POST"])
def redireccion():
    # Obtenemos la acción que el usuario ha seleccionado desde el formulario
    accion = request.form.get('action')
    
    # Dependiendo de la acción, redirige a diferentes secciones de la aplicación
    if accion == "facultades":
        return redirect("https://www.uexternado.edu.co/facultades/")  # Redirige a una página externa
    elif accion == "historial":
        return redirect(url_for('historial.indexHistorial'))  # Redirige al historial
    elif accion == "estadoEquipo":
        return redirect(url_for('equipo.estado_equipo'))  # Redirige al estado del equipo
    elif accion == "usuarios":
        return redirect(url_for('usuario.indexUsuario'))  # Redirige a los usuarios
    elif accion == "software":
        return redirect(url_for('software.indexSoftware'))  # Redirige a la sección de software

# Ruta para mostrar equipos en la sala "D507" con paginación
@bp.route("/D507")
def D507():
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto es 1
    per_page = 10  # Número de equipos por página
    
    # Cálculo del desplazamiento para la consulta (paginación)
    offset = (page - 1) * per_page
    
    # Consulta a la base de datos para obtener los equipos en la sala "D507" con paginación
    equipos_query = Equipo.query.filter_by(sala="D507").offset(offset).limit(per_page).all()
    
    # Total de equipos en la sala "D507" para la paginación
    total = Equipo.query.filter_by(sala="D507").count()
    
    # Renderiza la plantilla con los datos obtenidos
    return render_template("/prueba/salaD507.html", equipos=equipos_query, page=page, per_page=per_page, total=total)

# Ruta que devuelve los datos de equipos en la sala "D507" en formato JSON (con soporte para búsqueda y filtrado)
@bp.route("/D507_data")
def D507_data():
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto es 1
    per_page = 10  # Número de equipos por página
    
    # Obtener los parámetros de búsqueda y estado desde la URL
    search = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    
    # Cálculo del desplazamiento para la consulta (paginación)
    offset = (page - 1) * per_page
    
    # Construir la consulta con condiciones de búsqueda y filtrado
    query = Equipo.query.filter_by(sala="D507")
    if search:
        query = query.filter(Equipo.idEquipo.ilike(f"%{search}%"))  # Filtra por ID de equipo
    if estado:
        query = query.filter_by(estadoEquipo=estado)  # Filtra por estado del equipo
    
    # Ejecuta la consulta con paginación
    equipos_query = query.offset(offset).limit(per_page).all()
    
    # Total de equipos que cumplen los filtros
    total = query.count()
    
    # Prepara los datos para la respuesta en formato JSON
    items = [{'idEquipo': e.idEquipo, 'estadoEquipo': e.estadoEquipo} for e in equipos_query]
    
    # Devuelve la respuesta JSON con los datos de paginación
    return jsonify({
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page * per_page < total else None
    })

# Similar a la ruta de D507, pero para la sala "H405"
@bp.route("/H405")
def H405():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    equipos_query = Equipo.query.filter_by(sala="H405").offset(offset).limit(per_page).all()
    total = Equipo.query.filter_by(sala="H405").count()
    return render_template("/prueba/salaH405.html", equipos=equipos_query, page=page, per_page=per_page, total=total)

# Ruta para obtener datos de equipos en la sala "H405" con filtros y paginación
@bp.route("/H405_data")
def H405_data():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    offset = (page - 1) * per_page
    query = Equipo.query.filter_by(sala="H405")
    if search:
        query = query.filter(Equipo.idEquipo.ilike(f"%{search}%"))
    if estado:
        query = query.filter_by(estadoEquipo=estado)
    equipos_query = query.offset(offset).limit(per_page).all()
    total = query.count()
    items = [{'idEquipo': e.idEquipo, 'estadoEquipo': e.estadoEquipo} for e in equipos_query]
    return jsonify({
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page * per_page < total else None
    })

# Similar a la ruta de D507, pero para la sala "I408"
@bp.route("/I408")
def I408():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    equipos_query = Equipo.query.filter_by(sala="I408").offset(offset).limit(per_page).all()
    total = Equipo.query.filter_by(sala="I408").count()
    return render_template("/prueba/salaI408.html", equipos=equipos_query, page=page, per_page=per_page, total=total)

# Ruta para obtener datos de equipos en la sala "I408" con filtros y paginación
@bp.route("/I408_data")
def I408_data():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    offset = (page - 1) * per_page
    query = Equipo.query.filter_by(sala="I408")
    if search:
        query = query.filter(Equipo.idEquipo.ilike(f"%{search}%"))
    if estado:
        query = query.filter_by(estadoEquipo=estado)
    equipos_query = query.offset(offset).limit(per_page).all()
    total = query.count()
    items = [{'idEquipo': e.idEquipo, 'estadoEquipo': e.estadoEquipo} for e in equipos_query]
    return jsonify({
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page * per_page < total else None
    })

# Ruta para mostrar diseño de una página de prueba en formato celular
@bp.route("/celular")
def celular():
    return render_template("prueba/prueba_diseño_celular.html")

# Ruta para mostrar una página relacionada con computadoras
@bp.route("/computo")
def computo():
    return render_template("prueba/computo.html")