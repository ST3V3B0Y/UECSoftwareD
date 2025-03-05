# Importación de módulos necesarios para la aplicación web con Flask
from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError  # Para manejar errores de integridad en la base de datos
from app import db, login_manager  # db: instancia de SQLAlchemy, login_manager: manejo de sesión
from app.models import Software  # Importa el modelo Software de la base de datos

# Creación de un Blueprint llamado "software" que contiene las rutas relacionadas con los softwares
bp = Blueprint("software", __name__)

# Ruta para visualizar todos los softwares disponibles
@bp.route("/software",  methods=["GET"])
def indexSoftware():
    # Verifica si el usuario está autenticado
    if current_user.is_authenticated:
        if request.method == "GET":
            # Consulta todos los registros de la tabla Software
            softwares = Software.query.all()
            print("softwares: ", softwares)  # Para depuración, muestra los softwares en consola
            # Devuelve la vista HTML, pasando los softwares como variable
            return render_template("/administracion/software/index.html", software=softwares)
    else:
        # Si el usuario no está autenticado, muestra un mensaje de error y redirige al login
        flash("Inicie sesion para continuar...", "error")
        return redirect(url_for('usuario.login_administracion'))

# Ruta para eliminar un software mediante una solicitud POST
@bp.route("/software/eliminar", methods=["POST"])
def eliminar_software():
    # Verifica si el usuario está autenticado
    if current_user.is_authenticated:
        if request.method == "POST":
            # Recibe los datos en formato JSON
            data = request.get_json()
            # Extrae el ID del software a eliminar
            idSoftware = data.get("idSoftware")
            
            # Busca el software con el ID proporcionado en la base de datos
            software = Software.query.filter_by(idSoftware=idSoftware).first()
            
            if software:
                try:
                    # Si el software existe, elimina el registro de la base de datos
                    db.session.delete(software)
                    db.session.commit()  # Realiza el commit para confirmar la eliminación
                    # Responde con un mensaje de éxito en formato JSON
                    return jsonify({"status": "success", "message": f"Software eliminado correctamente."})
                except Exception as e:
                    # Si ocurre un error, revierte la transacción
                    db.session.rollback()
                    # Responde con un mensaje de error si la eliminación falla
                    return jsonify({"status": "error", "message": f"Error al eliminar software: {str(e)}"})
            else:
                # Si el software no se encuentra, responde con un error indicando que no existe
                return jsonify({"status": "error", "message": f"Software con ID {idSoftware} no encontrado."})

# Ruta para agregar un nuevo software mediante una solicitud POST
@bp.route("/software/nuevo", methods=["POST"])
def nuevo_software():
    # Verifica si el usuario está autenticado
    if current_user.is_authenticated:
        if request.method == "POST":
            # Recibe los datos en formato JSON
            data = request.get_json()
            # Extrae el nombre del software desde los datos
            nombreSoftware = data.get("nombreSoftware")
            
            # Verifica si ya existe un software con el mismo nombre
            software = Software.query.filter_by(nombreSoftware=nombreSoftware).first()
            
            if not software:
                try:
                    # Si no existe, crea una nueva instancia del software con el nombre proporcionado
                    software = Software(nombreSoftware=nombreSoftware)
                    # Añade el software a la sesión de la base de datos
                    db.session.add(software)
                    # Realiza el commit para guardar los cambios en la base de datos
                    db.session.commit()
                    # Responde con un mensaje de éxito
                    return jsonify({"status": "success", "message": f"Software agregado correctamente."})
                except Exception as e:
                    # Si ocurre un error, revierte la transacción
                    db.session.rollback()
                    # Responde con un mensaje de error si la adición falla
                    return jsonify({"status": "error", "message": f"Error al agregar software."})
            else:
                # Si ya existe un software con ese nombre, responde con un error
                return jsonify({"status": "error", "message": f"El software {nombreSoftware} ya existe."})
