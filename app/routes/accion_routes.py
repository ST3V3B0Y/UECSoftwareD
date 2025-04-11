from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Equipo
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

bp = Blueprint("accion", __name__, url_prefix="/accion")

class ManejadorSalas:
    """Clase auxiliar para manejar operaciones relacionadas con salas"""
    
    @staticmethod
    def obtener_equipos(sala, pagina=1, por_pagina=10, busqueda=None, estado=None):
        """
        Obtiene lista paginada de equipos para una sala con filtros opcionales
        
        Args:
            sala (str): Código de sala (ej. 'D507')
            pagina (int): Número de página actual
            por_pagina (int): Elementos por página
            busqueda (str): Término de búsqueda para ID de equipo
            estado (str): Filtro por estado de equipo
            
        Returns:
            tuple: (equipos_query, total)
        """
        offset = (pagina - 1) * por_pagina
        query = Equipo.query.filter_by(sala=sala)
        
        if busqueda:
            query = query.filter(Equipo.idEquipo.ilike(f"%{busqueda}%"))
        if estado:
            query = query.filter_by(estadoEquipo=estado)
            
        return (
            query.offset(offset).limit(por_pagina).all(),
            query.count()
        )

    @staticmethod
    def crear_respuesta(items, pagina, por_pagina, total):
        """Crea respuesta JSON estandarizada para datos paginados"""
        return jsonify({
            'items': items,
            'total': total,
            'page': pagina,
            'per_page': por_pagina,
            'has_prev': pagina > 1,
            'has_next': pagina * por_pagina < total,
            'prev_num': pagina - 1 if pagina > 1 else None,
            'next_num': pagina + 1 if pagina * por_pagina < total else None
        })

@login_required
@bp.route("", methods=["GET", "POST"])
def redireccion():
    """
    Maneja redirecciones basadas en acciones del formulario
    
    Rutas disponibles:
    - facultades: Redirige a página de facultades
    - historial: Redirige al índice de historial
    - estadoEquipo: Redirige al estado de equipos
    - usuarios: Redirige al índice de usuarios
    - software: Redirige al índice de software
    """
    accion = request.form.get('action')
    mapa_redireccion = {
        "facultades": "https://www.uexternado.edu.co/facultades/",
        "historial": 'historial.indexHistorial',
        "estadoEquipo": 'equipo.estado_equipo',
        "usuarios": 'usuario.indexUsuario',
        "software": 'software.indexSoftware'
    }
    
    if accion in mapa_redireccion:
        destino = mapa_redireccion[accion]
        return redirect(destino if 'http' in destino else url_for(destino))
    
    return redirect(url_for('main.index'))

@bp.route("/D507")
def D507():
    """Renderiza la página de equipos de la sala D507 con paginación"""
    pagina = request.args.get('page', 1, type=int)
    equipos, total = ManejadorSalas.obtener_equipos("D507", pagina=pagina)
    return render_template("prueba/salaD507.html", 
                         equipos=equipos,
                         page=pagina,
                         per_page=10,
                         total=total)

@bp.route("/D507_data")
def D507_data():
    """Endpoint JSON para datos de equipos en D507 con búsqueda y filtros"""
    pagina = request.args.get('page', 1, type=int)
    busqueda = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    
    equipos, total = ManejadorSalas.obtener_equipos(
        "D507",
        pagina=pagina,
        busqueda=busqueda,
        estado=estado
    )
    
    items = [{
        'idEquipo': e.idEquipo,
        'estadoEquipo': e.estadoEquipo,
        'ipEquipo': e.ipEquipo  # Se agregó la IP como referencia
    } for e in equipos]
    
    return ManejadorSalas.crear_respuesta(items, pagina, 10, total)

# Rutas optimizadas similares para H405 e I408
@bp.route("/H405")
def H405():
    """Renderiza la página de equipos de la sala H405 con paginación"""
    pagina = request.args.get('page', 1, type=int)
    equipos, total = ManejadorSalas.obtener_equipos("H405", pagina=pagina)
    return render_template("prueba/salaH405.html",
                         equipos=equipos,
                         page=pagina,
                         per_page=10,
                         total=total)

@bp.route("/H405_data")
def H405_data():
    """Endpoint JSON para datos de equipos en H405"""
    pagina = request.args.get('page', 1, type=int)
    busqueda = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    
    equipos, total = ManejadorSalas.obtener_equipos(
        "H405",
        pagina=pagina,
        busqueda=busqueda,
        estado=estado
    )
    
    items = [{
        'idEquipo': e.idEquipo,
        'estadoEquipo': e.estadoEquipo,
        'ipEquipo': e.ipEquipo
    } for e in equipos]
    
    return ManejadorSalas.crear_respuesta(items, pagina, 10, total)

@bp.route("/I408")
def I408():
    """Renderiza la página de equipos de la sala I408 con paginación"""
    pagina = request.args.get('page', 1, type=int)
    equipos, total = ManejadorSalas.obtener_equipos("I408", pagina=pagina)
    return render_template("prueba/salaI408.html",
                         equipos=equipos,
                         page=pagina,
                         per_page=10,
                         total=total)

@bp.route("/I408_data")
def I408_data():
    """Endpoint JSON para datos de equipos en I408"""
    pagina = request.args.get('page', 1, type=int)
    busqueda = request.args.get('search', '', type=str)
    estado = request.args.get('estado', '', type=str)
    
    equipos, total = ManejadorSalas.obtener_equipos(
        "I408",
        pagina=pagina,
        busqueda=busqueda,
        estado=estado
    )
    
    items = [{
        'idEquipo': e.idEquipo,
        'estadoEquipo': e.estadoEquipo,
        'ipEquipo': e.ipEquipo
    } for e in equipos]
    
    return ManejadorSalas.crear_respuesta(items, pagina, 10, total)

@bp.route("/celular")
def celular():
    """Vista para pruebas en dispositivos móviles"""
    return render_template("prueba/prueba_diseño_celular.html")

@bp.route("/computo")
def computo():
    """Vista para sala de cómputo"""
    return render_template("prueba/computo.html")