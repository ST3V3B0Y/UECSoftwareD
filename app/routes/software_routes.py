from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError  # Para manejar errores de integridad de la base de datos
from app import db, login_manager  # Importa la instancia de la base de datos y el login manager
from app.models import Software  # Importa el modelo de Software

# Crea un Blueprint llamado 'software' para agrupar rutas relacionadas
bp = Blueprint("software", __name__)


@bp.route("/software", methods=["GET"])
def indexSoftware():
    """
    Ruta principal para gestionar software.
    
    Funcionalidades:
    - GET: Muestra todos los softwares registrados
    - Control de acceso: Requiere autenticación, sino redirige a login
    
    Retorna:
    - Template HTML con la lista de softwares
    """
    
    if current_user.is_authenticated:
        if request.method == "GET":
            # Consulta todos los softwares en la base de datos
            softwares = Software.query.all()
            return render_template("/administracion/software/index.html", software=softwares)
    else:
        flash("Inicie sesión para continuar...", "error")
        return redirect(url_for('usuario.login_administracion'))


@bp.route("/software/eliminar", methods=["POST"])
def eliminar_software():
    """
    Elimina un software existente.
    
    Parámetros (JSON):
    - idSoftware: ID del software a eliminar
    
    Retorna:
    - JSON con estado de la operación:
      - success: Software eliminado correctamente
      - error: Mensaje descriptivo del error
    """
    
    if current_user.is_authenticated:
        if request.method == "POST":
            data = request.get_json()  # Obtiene los datos en formato JSON
            idSoftware = data.get("idSoftware")  # Extrae el ID del software
            
            # Busca el software en la base de datos
            software = Software.query.filter_by(idSoftware=idSoftware).first()
            
            if software:
                try:
                    db.session.delete(software)  # Elimina el registro
                    db.session.commit()  # Confirma los cambios
                    return jsonify({
                        "status": "success", 
                        "message": "Software eliminado correctamente."
                    })
                except Exception as e:
                    db.session.rollback()  # Revierte los cambios en caso de error
                    return jsonify({
                        "status": "error", 
                        "message": f"Error al eliminar software: {str(e)}"
                    })
            else:
                return jsonify({
                    "status": "error", 
                    "message": f"Software con ID {idSoftware} no encontrado."
                })


@bp.route("/software/nuevo", methods=["POST"])
def nuevo_software():
    """
    Agrega un nuevo software al sistema.
    
    Parámetros (JSON):
    - nombreSoftware: Nombre del nuevo software
    
    Retorna:
    - JSON con estado de la operación:
      - success: Software agregado correctamente
      - error: Mensaje descriptivo del error (ya existe u otro error)
    """
    
    if current_user.is_authenticated:
        if request.method == "POST":
            data = request.get_json()  # Obtiene los datos en formato JSON
            nombreSoftware = data.get("nombreSoftware")  # Extrae el nombre del software
            
            # Verifica si el software ya existe
            software = Software.query.filter_by(nombreSoftware=nombreSoftware).first()
            
            if not software:
                try:
                    # Crea y guarda el nuevo software
                    nuevo_software = Software(nombreSoftware=nombreSoftware)
                    db.session.add(nuevo_software)
                    db.session.commit()
                    return jsonify({
                        "status": "success", 
                        "message": "Software agregado correctamente."
                    })
                except Exception as e:
                    db.session.rollback()
                    return jsonify({
                        "status": "error", 
                        "message": "Error al agregar software"
                    })
            else:
                return jsonify({
                    "status": "error", 
                    "message": f"El software {nombreSoftware} ya existe."
                })