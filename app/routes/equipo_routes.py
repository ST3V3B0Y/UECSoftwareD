# Importaciones de Flask y extensiones relacionadas
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from app import db  # Instancia de la base de datos SQLAlchemy
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError  # Para manejar errores de integridad de la base de datos
from sqlalchemy import or_  # Para consultas OR en SQLAlchemy
from datetime import datetime  # Para manejar fechas y horas
from app.models import Equipo, Historial, Usuario, Software  # Modelos de la base de datos
import socket, json, threading  # Para comunicación de red y manejo de hilos
from app.config import SERVER_HOST, SERVER_PORT  # Configuración del servidor

# Creación de un Blueprint para las rutas relacionadas con equipos
bp = Blueprint("equipo", __name__)

# Ruta principal para manejar equipos
@bp.route("/equipo", methods=["GET", "POST"])
@login_required  # Requiere que el usuario esté autenticado
def equipo():
    if request.method == "GET":
        usuario = current_user  # Obtiene el usuario actual
        equipos = Equipo.query.all()  # Consulta todos los equipos
        software = Software.query.all()  # Consulta todo el software
        # Crea una lista de diccionarios con información del software
        software_list = [{"idSoftware": s.idSoftware, "nombreSoftware": s.nombreSoftware} for s in software]
        # Renderiza la plantilla con los datos
        return render_template(
            "administracion/equipo/main.html", usuario=usuario, equipos=equipos, software=software_list
        )

# Ruta para pedir un equipo
@bp.route("/equipo/pedir_equipo", methods=["GET", "POST"])
@login_required
def pedir_equipo():
    if request.method == "POST":
        data = request.get_json()  # Obtiene los datos JSON de la solicitud
        pc = data.get('pc')  # ID del equipo
        software_seleccionado = request.form.get('software')  # Software seleccionado desde el formulario
        software = data.get('softwareId')  # ID del software desde JSON
        otroSoftware = data.get('otroSoftware')  # Campo para software no listado

        print("Datos recibidos:", data)
        try:
            # Verifica si el usuario ya tiene un equipo asignado sin hora de finalización
            noRepeatUser = Historial.query.filter(Historial.Usuario_idUsuario==current_user.idUsuario, Historial.horaFin==None).first()
            if noRepeatUser:
                return jsonify({"status": "warning", "message": "El usuario ya tiene asignado un equipo"})

            # Obtiene el equipo y cambia su estado a "usado"
            equipo = Equipo.query.filter_by(idEquipo=pc).first()
            equipo.estadoEquipo = "usado"
            
            # Valida que se haya seleccionado un software
            if software_seleccionado==0:
                return jsonify({"status": "warning", "message": "Por favor selecciona un software"})
            else: 
                # Crea un registro de historial dependiendo de si hay software adicional
                if otroSoftware is None:
                    registro = Historial(
                        Usuario_idUsuario=current_user.idUsuario,
                        horaInicio=datetime.now().strftime('%H:%M:%S'),
                        Equipo_idEquipo=pc,
                        nombreSala="D507",
                        software_idSoftware=software
                    )
                else:
                    registro = Historial(
                        Usuario_idUsuario=current_user.idUsuario,
                        horaInicio=datetime.now().strftime('%H:%M:%S'),
                        Equipo_idEquipo=pc,
                        nombreSala="D507",
                        software_idSoftware=software,
                        otroSoftware=otroSoftware
                    )
            
            # Guarda los cambios en la base de datos
            db.session.add(registro)
            db.session.add(equipo)
            db.session.commit()

            return jsonify({"status": "success", "message": f"Computador {pc} registrado y desbloqueado correctamente."})
        except IntegrityError as e:
            print("error en registro pc: ", e)
            db.session.rollback()  # Revierte los cambios en caso de error
            return jsonify({"status": "error", "message": "Complete todos los campos"})

# Ruta para ver el estado de los equipos
@bp.route("/equipo/estado_equipo", methods=["GET", "POST"])
def estado_equipo():
    if current_user.is_authenticated:  # Verifica autenticación
        if request.method == "POST":
            equipo_a_buscar = request.form.get('equipo')  # Obtiene criterio de búsqueda
            # Consulta compleja para buscar equipos en uso
            buscar = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Equipo.sala, Software.nombreSoftware, Historial.otroSoftware, Historial.Usuario_idUsuario, Historial.fecha)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin == None)  # Solo equipos sin hora de finalización
                .filter(or_(
                    Equipo.idEquipo==equipo_a_buscar,
                    Usuario.nombreUsuario.ilike(f"%{equipo_a_buscar}%"),
                    Usuario.identificacionUsuario==equipo_a_buscar
                    )
                )
                .order_by(Historial.fecha.desc(), Historial.horaInicio.desc())
                .all()
            )
            print("consulta para buscar",buscar)
            cantidadEquipos = len(buscar)
            return render_template("administracion/estadoEquipo/index.html", equipos_usados=buscar, cantidad_equipos=cantidadEquipos)
        else:
            # Consulta todos los equipos en uso si no hay criterio de búsqueda
            equiposUsados = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Equipo.sala, Software.nombreSoftware, Historial.otroSoftware, Historial.Usuario_idUsuario, Historial.fecha)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin == None)
                .order_by(Historial.fecha.desc(), Historial.horaInicio.desc())
                .all()
            )
            print("informacion de la tabla",equiposUsados)
            cantidadEquipos = len(equiposUsados)
            return render_template("administracion/estadoEquipo/index.html", equipos_usados=equiposUsados, cantidad_equipos=cantidadEquipos)
    else:
        return redirect(url_for('usuario.login_administracion'))  # Redirige si no está autenticado

# Ruta para liberar un equipo específico
@bp.route("/equipo/liberar_equipo/<int:idEquipo>", methods=["POST"])
def liberar_equipo(idEquipo):
    if current_user.is_authenticated:
        data = request.json  # Obtiene el cuerpo JSON de la petición
        idUsuario = data.get('idUsuario')  # Obtiene el idUsuario

        # Busca el equipo y el registro de historial correspondiente
        equipo_a_editar = Equipo.query.filter_by(idEquipo=idEquipo).first()
        editar_historial = Historial.query.filter_by(Usuario_idUsuario=idUsuario, Equipo_idEquipo=idEquipo, horaFin=None).first_or_404()

        # Actualiza los campos
        equipo_a_editar.estadoEquipo = "libre"
        editar_historial.horaFin = datetime.now().strftime('%H:%M:%S')  # Establece hora de finalización

        try:
            db.session.commit()  # Guarda los cambios
            return jsonify({'success': True, 'message': 'Historial actualizado con la fecha y hora actuales.'})
        except Exception as e:
            db.session.rollback()  # Revierte en caso de error
            print("error en la actualizacion: ", e)
            return jsonify({'success': False, 'message': 'Error al actualizar el historial.'})
    else:
        return jsonify({'success': False, 'message': 'No estás autenticado.'})

# Ruta para liberar todos los equipos de la sala D507
@bp.route("/equipo/liberar_todo/", methods=["POST"])
def liberar_todo():
    if current_user.is_authenticated:
        # Obtiene todos los registros de historial y equipos sin liberar en D507
        editar_historial_D507 = Historial.query.filter(Historial.horaFin==None, Equipo.sala=="D507").all()
        editar_equipo_D507 = Equipo.query.filter(Equipo.estadoEquipo=="usado", Equipo.sala=="D507").all()

        # Libera todos los equipos
        for equipo in editar_equipo_D507:
            equipo.estadoEquipo = "libre"

        # Establece hora de finalización para todos los registros
        for historial in editar_historial_D507:
            historial.horaFin = datetime.now().strftime('%H:%M:%S')

        try:
            db.session.commit()  # Guarda los cambios
            return jsonify({'success': True, 'message': 'Historial actualizado con la fecha y hora actuales.'})
        except Exception as e:
            db.session.rollback()  # Revierte en caso de error
            print("error en la actualizacion: ", e)
            return jsonify({'success': False, 'message': 'Error al actualizar el historial.'})
    else:
        return jsonify({'success': False, 'message': 'No estás autenticado.'})