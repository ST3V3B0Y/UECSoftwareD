# Importación de librerías necesarias
# flask: Framework para crear la aplicación web y manejar rutas.
# flask_login: Módulo para gestionar la autenticación de usuarios.
# sqlalchemy: ORM para interactuar con la base de datos MySQL.
# datetime: Para trabajar con fechas y horas.
# socket: Usado para la comunicación en red, aunque no se usa explícitamente en este código.
# json: Para manejar datos en formato JSON.
# threading: Usado para manejar operaciones en segundo plano, pero no se usa explícitamente en este código.
# app.config: Configuración de la aplicación, donde se encuentran los detalles de la conexión al servidor.

from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from app import db
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime
from app.models import Equipo
from app.models import Historial
from app.models import Usuario
from app.models import Software
import socket
import json
import threading
from app.config import SERVER_HOST, SERVER_PORT

# Definición del Blueprint para manejar las rutas relacionadas con los equipos
bp = Blueprint("equipo", __name__)

# Ruta para mostrar el estado de los equipos y permitir asignar software
@bp.route("/equipo", methods=["GET", "POST"])
@login_required  # Solo los usuarios autenticados pueden acceder
def equipo():
    if request.method == "GET":
        # Se obtiene el usuario actual y todos los equipos y software disponibles
        usuario = current_user
        equipos = Equipo.query.all()
        software = Software.query.all()
        software_list = [{"idSoftware": s.idSoftware, "nombreSoftware": s.nombreSoftware} for s in software]
        
        # Renderiza la plantilla de administración de equipos con la información de los equipos y software
        return render_template(
            "administracion/equipo/main.html", usuario=usuario, equipos=equipos, software=software_list
        )

# Ruta para pedir un equipo (asignación de equipo a un usuario)
@bp.route("/equipo/pedir_equipo", methods=["GET", "POST"])
@login_required  # Solo los usuarios autenticados pueden acceder
def pedir_equipo():
    if request.method == "POST":
        # Obtiene los datos enviados como JSON
        data = request.get_json()
        pc = data.get('pc')  # ID del equipo solicitado
        software_seleccionado = request.form.get('software')  # ID del software seleccionado
        software = data.get('softwareId')  # ID del software
        otroSoftware = data.get('otroSoftware')  # Otro software, si aplica

        print("Datos recibidos:", data)
        try:
            # Verifica si el usuario ya tiene un equipo asignado
            noRepeatUser = Historial.query.filter(Historial.Usuario_idUsuario==current_user.idUsuario, Historial.horaFin==None).first()
            if noRepeatUser:
                return jsonify({"status": "warning", "message": "El usuario ya tiene asignado un equipo"})

            # Busca el equipo solicitado en la base de datos
            equipo = Equipo.query.filter_by(idEquipo=pc).first()
            equipo.estadoEquipo = "usado"  # Marca el equipo como usado

            if software_seleccionado == 0:
                return jsonify({"status": "warning", "message": "Por favor selecciona un software"})
            else:
                # Crea un nuevo registro en el historial
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
            
            # Guarda el registro en el historial y el cambio de estado del equipo
            db.session.add(registro)
            db.session.add(equipo)
            db.session.commit()

            return jsonify({"status": "success", "message": f"Computador {pc} registrado y desbloqueado correctamente."})
        except IntegrityError as e:
            print("error en registro pc: ", e)
            db.session.rollback()  # Si hay error, se revierte la transacción
            return jsonify({"status": "error", "message": "Complete todos los campos"})

# Ruta para ver el estado de los equipos (quién los está usando, qué software tiene)
@bp.route("/equipo/estado_equipo", methods=["GET", "POST"])
def estado_equipo():
    if current_user.is_authenticated:
        if request.method == "POST":
            equipo_a_buscar = request.form.get('equipo')  # Parámetro de búsqueda (por ID o nombre de usuario)
            buscar = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Equipo.sala, Software.nombreSoftware, Historial.otroSoftware, Historial.Usuario_idUsuario, Historial.fecha)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin == None)  # Filtra solo los registros activos (sin hora de fin)
                .filter(or_(
                    Equipo.idEquipo == equipo_a_buscar,
                    Usuario.nombreUsuario.ilike(f"%{equipo_a_buscar}%"),
                    Usuario.identificacionUsuario == equipo_a_buscar
                ))
                .order_by(Historial.fecha.desc(), Historial.horaInicio.desc())  # Ordena por fecha y hora
                .all()
            )
            cantidadEquipos = len(buscar)
            return render_template("administracion/estadoEquipo/index.html", equipos_usados=buscar, cantidad_equipos=cantidadEquipos)
        else:
            # Si es un GET, se muestra el estado de todos los equipos
            equiposUsados = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Equipo.sala, Software.nombreSoftware, Historial.otroSoftware, Historial.Usuario_idUsuario, Historial.fecha)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin == None)  # Filtra solo los registros activos
                .order_by(Historial.fecha.desc(), Historial.horaInicio.desc())  # Ordena por fecha y hora
                .all()
            )
            cantidadEquipos = len(equiposUsados)
            return render_template("administracion/estadoEquipo/index.html", equipos_usados=equiposUsados, cantidad_equipos=cantidadEquipos)
    else:
        return redirect(url_for('usuario.login_administracion'))  # Redirige si no está autenticado

# Ruta para liberar un equipo (finalizar su uso y liberar el equipo)
@bp.route("/equipo/liberar_equipo/<int:idEquipo>", methods=["POST"])
def liberar_equipo(idEquipo):
    if current_user.is_authenticated:
        data = request.json  # Obtiene el cuerpo JSON de la petición
        idUsuario = data.get('idUsuario')  # Obtiene el idUsuario

        equipo_a_editar = Equipo.query.filter_by(idEquipo=idEquipo).first()  # Busca el equipo a editar
        editar_historial = Historial.query.filter_by(Usuario_idUsuario=idUsuario, Equipo_idEquipo=idEquipo, horaFin=None).first_or_404()  # Busca el historial del usuario con ese equipo

        # Actualiza el estado del equipo y la hora de finalización del historial
        equipo_a_editar.estadoEquipo = "libre"
        editar_historial.horaFin = datetime.now().strftime('%H:%M:%S')

        try:
            db.session.commit()  # Guarda los cambios en la base de datos
            return jsonify({'success': True, 'message': 'Historial actualizado con la fecha y hora actuales.'})
        except Exception as e:
            db.session.rollback()  # Revertimos en caso de error
            print("error en la actualizacion: ", e)
            return jsonify({'success': False, 'message': 'Error al actualizar el historial.'})
    else:
        return jsonify({'success': False, 'message': 'No estás autenticado.'})

# Ruta para liberar todos los equipos de la sala "D507"
@bp.route("/equipo/liberar_todo/", methods=["POST"])
def liberar_todo():
    if current_user.is_authenticated:
        # Filtra todos los registros de equipos usados en la sala "D507"
        editar_historial_D507 = Historial.query.filter(Historial.horaFin == None, Equipo.sala == "D507").all()
        editar_equipo_D507 = Equipo.query.filter(Equipo.estadoEquipo == "usado", Equipo.sala == "D507").all()

        # Cambia el estado de los equipos a "libre" y actualiza la hora de fin en el historial
        for equipo in editar_equipo_D507:
            equipo.estadoEquipo = "libre"

        for historial in editar_historial_D507:
            historial.horaFin = datetime.now().strftime('%H:%M:%S')

        try:
            db.session.commit()  # Guarda los cambios en la base de datos
            return jsonify({'success': True, 'message': 'Historial actualizado con la fecha y hora actuales.'})
        except Exception as e:
            db.session.rollback()  # Revertimos en caso de error
            print("error en la actualizacion: ", e)
            return jsonify({'success': False, 'message': 'Error al actualizar el historial.'})
    else:
        return jsonify({'success': False, 'message': 'No estás autenticado.'})
