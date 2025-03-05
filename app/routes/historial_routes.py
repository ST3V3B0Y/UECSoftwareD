# Importación de librerías necesarias
# flask: Framework para manejar rutas y vistas en la aplicación web.
# db: Instancia de la base de datos de la aplicación.
# openpyxl: Librería para manejar archivos de Excel.
# datetime: Para manejar fechas y horas.
# os: Para operaciones del sistema como guardar archivos.
# flask_login: Para manejar sesiones de usuarios autenticados.
# sqlalchemy: ORM de SQL para interactuar con la base de datos.

from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask import send_file
from app import db
from sqlalchemy import or_
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from openpyxl import Workbook
from datetime import datetime
import os
from app.models import Historial
from app.models import Equipo
from app.models import Usuario
from app.models import Software
from app.models import Facultad

# Definición del Blueprint para manejar las rutas relacionadas con el historial
bp = Blueprint("historial", __name__)

# Ruta para ver el historial de equipos asignados
@bp.route("/historial", methods=['GET','POST'])
def indexHistorial():
    # Verifica si el usuario está autenticado
    if current_user.is_authenticated:
        # Si el método de la solicitud es POST, realiza una búsqueda por usuario o equipo
        if request.method == 'POST':
            persona_a_buscar = request.form.get('usuario')
            el_historial = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Historial.horaFin, Historial.fecha, Historial.nombreSala, Historial.Usuario_idUsuario, Software.nombreSoftware, Historial.otroSoftware)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin.isnot(None))  # Filtra registros donde horaFin no es nulo
                .filter(
                    or_(
                        Equipo.idEquipo == persona_a_buscar,  # Filtra por ID de equipo con coincidencia exacta
                        Usuario.nombreUsuario.ilike(f"%{persona_a_buscar}%"),  # Filtra por nombre de usuario
                        Usuario.identificacionUsuario == persona_a_buscar  # Filtra por identificación
                    )
                ).all()
            )
            return render_template("administracion/historial/index.html", historial=el_historial)
        
        # Si el método es GET, muestra todos los registros de historial
        if request.method == 'GET':
            el_historial = (
                db.session.query(Usuario.nombreUsuario, Usuario.identificacionUsuario, Equipo.idEquipo, Historial.horaInicio, Historial.horaFin, Historial.fecha, Historial.nombreSala, Historial.Usuario_idUsuario, Software.nombreSoftware, Historial.otroSoftware)
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin.isnot(None))  # Filtra registros donde horaFin no es nulo
                .order_by(Historial.fecha.asc(), Historial.horaFin.desc())  # Ordena por fecha y hora de fin
                .all()
            )
            return render_template('administracion/historial/index.html', historial=el_historial)
    else:
        return redirect(url_for('usuario.login_administracion'))  # Redirige al login si el usuario no está autenticado

# Ruta para generar un informe en formato Excel de los registros de historial
@bp.route("/historial/generar_informe", methods=["POST"])
def generar_informe():
    data = request.json  # Obtiene el cuerpo JSON de la solicitud
    fechaInicio = data.get('fechaInicio')
    fechaFinal = data.get('fechaFin')

    # Verifica que las fechas no estén vacías
    if not fechaInicio or not fechaFinal:
        return jsonify({"status": "error", "message": "Las fechas no pueden ser vacías."}), 400

    # Convierte las fechas de cadena a objeto datetime
    fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d')
    fechaFinal = datetime.strptime(fechaFinal, '%Y-%m-%d')

    # Consulta los registros de historial en el rango de fechas indicado
    el_historial = db.session.query(
        Usuario.nombreUsuario,
        Usuario.identificacionUsuario,
        Facultad.nombreFacultad,
        Equipo.idEquipo,
        Historial.horaInicio,
        Historial.horaFin,
        Historial.fecha,
        Historial.nombreSala,
        Software.nombreSoftware,
        Historial.otroSoftware
    ).join(Usuario, Historial.Usuario_idUsuario == Usuario.idUsuario) \
     .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo) \
     .join(Software, Historial.software_idSoftware == Software.idSoftware) \
     .join(Facultad, Usuario.Facultad_idFacultad == Facultad.idFacultad) \
     .filter(Historial.horaFin.isnot(None)) \
     .filter(Historial.fecha.between(fechaInicio, fechaFinal)) \
     .all()

    # Crear un libro de trabajo de Excel y agregar encabezados
    wb = Workbook()
    ws = wb.active
    ws.append([
        "Nombre Usuario", "Identificación", "Facultad", "ID Equipo", 
        "Hora Inicio", "Hora Fin", "Fecha", "Nombre Sala", "Nombre Software", "Otro Software"
    ])

    # Agregar los registros obtenidos a la hoja de Excel
    for registro in el_historial:
        ws.append(list(registro))

    # Generar el nombre del archivo Excel con la fecha actual
    fecha_actual = datetime.now().strftime('%d-%m-%y')
    documentos_path = os.path.join(os.path.expanduser('~'), 'Documents')  # Carpeta 'Documents'
    nombre_archivo = os.path.join(documentos_path, f'informe {fecha_actual}.xlsx')

    # Verifica si el archivo ya existe y agrega un número al nombre si es necesario
    contador = 1
    while os.path.exists(nombre_archivo):
        nombre_archivo = os.path.join(documentos_path, f'informe {fecha_actual} ({contador}).xlsx')
        contador += 1

    # Guarda el archivo de Excel generado
    try:
        wb.save(nombre_archivo)
        return jsonify({"status": "success", "message": f"Reporte creado exitosamente en la carpeta 'Documentos'."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al crear el reporte: {str(e)}"})
