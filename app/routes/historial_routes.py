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
from openpyxl import Workbook  # Biblioteca para crear archivos Excel
from datetime import datetime  # Para manejo de fechas
import os  # Para operaciones con el sistema de archivos
from app.models import Historial  # Modelo de historial de uso
from app.models import Equipo  # Modelo de equipos
from app.models import Usuario  # Modelo de usuarios
from app.models import Software  # Modelo de software
from app.models import Facultad  # Modelo de facultades


# Crea un Blueprint llamado 'historial' para agrupar rutas relacionadas
bp = Blueprint("historial", __name__)


@bp.route("/historial", methods=['GET','POST'])
def indexHistorial():
    """
    Ruta principal para visualizar el historial de uso.
    
    Funcionalidades:
    - GET: Muestra todos los registros históricos ordenados por fecha
    - POST: Filtra registros según parámetros de búsqueda
    - Control de acceso: Requiere autenticación, sino redirige a login
    
    Retorna:
    - Template HTML con los registros del historial
    """
    
    # Verifica si el usuario está autenticado
    if current_user.is_authenticated:
        
        # Manejo de búsquedas (POST)
        if request.method=='POST':
            # Obtiene término de búsqueda del formulario
            persona_a_buscar = request.form.get('usuario')
            
            # Consulta compleja que une múltiples tablas y aplica filtros
            el_historial = (
                db.session.query(
                    Usuario.nombreUsuario, 
                    Usuario.identificacionUsuario, 
                    Equipo.idEquipo, 
                    Historial.horaInicio, 
                    Historial.horaFin, 
                    Historial.fecha, 
                    Historial.nombreSala, 
                    Historial.Usuario_idUsuario, 
                    Software.nombreSoftware, 
                    Historial.otroSoftware
                )
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin.isnot(None))  # Solo registros completados
                .filter(
                    or_(
                        Equipo.idEquipo==persona_a_buscar,  # Búsqueda por ID de equipo
                        Usuario.nombreUsuario.ilike(f"%{persona_a_buscar}%"),  # Búsqueda parcial por nombre
                        Usuario.identificacionUsuario == persona_a_buscar  # Búsqueda exacta por identificación
                    )
                ).all()
            )
            
            return render_template("administracion/historial/index.html", historial=el_historial)
        
        # Manejo de vista general (GET)
        if request.method=='GET':
            # Consulta que obtiene todos los registros ordenados
            el_historial = (
                db.session.query(
                    Usuario.nombreUsuario, 
                    Usuario.identificacionUsuario, 
                    Equipo.idEquipo, 
                    Historial.horaInicio, 
                    Historial.horaFin, 
                    Historial.fecha, 
                    Historial.nombreSala, 
                    Historial.Usuario_idUsuario, 
                    Software.nombreSoftware, 
                    Historial.otroSoftware
                )
                .join(Historial, Historial.Usuario_idUsuario == Usuario.idUsuario)
                .join(Equipo, Historial.Equipo_idEquipo == Equipo.idEquipo)
                .join(Software, Historial.software_idSoftware == Software.idSoftware)
                .filter(Historial.horaFin.isnot(None))  # Solo registros completados
                .order_by(Historial.fecha.desc(), Historial.horaFin.desc())  # Orden descendente
                .all()
            )
            
            return render_template('administracion/historial/index.html', historial=el_historial)
    
    # Redirección si no está autenticado
    else:
        return redirect(url_for('usuario.login_administracion'))


@bp.route("/historial/generar_informe", methods=["POST"])
def generar_informe():
    """
    Genera un informe en Excel con registros históricos filtrados por fechas.
    
    Parámetros (JSON):
    - fechaInicio: Fecha inicial del rango (formato YYYY-MM-DD)
    - fechaFin: Fecha final del rango (formato YYYY-MM-DD)
    
    Retorna:
    - JSON con estado de la operación y mensaje
    - En caso de éxito: guarda el archivo en la carpeta Documentos del usuario
    """
    
    # Obtiene datos del request
    data = request.json
    fechaInicio = data.get('fechaInicio')
    fechaFinal = data.get('fechaFin')

    # Validación de fechas
    if not fechaInicio or not fechaFinal:
        return jsonify({
            "status": "error", 
            "message": "Las fechas no pueden ser vacías."
        }), 400

    # Conversión de fechas a objetos datetime
    fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d')
    fechaFinal = datetime.strptime(fechaFinal, '%Y-%m-%d')

    # Consulta con filtro por rango de fechas
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

    # Creación del archivo Excel
    wb = Workbook()  # Nuevo libro de Excel
    ws = wb.active  # Hoja activa

    # Encabezados del informe
    ws.append([
        "Nombre Usuario", 
        "Identificación", 
        "Facultad", 
        "ID Equipo", 
        "Hora Inicio", 
        "Hora Fin", 
        "Fecha", 
        "Nombre Sala", 
        "Nombre Software", 
        "Otro Software"
    ])

    # Llenado de datos
    for registro in el_historial:
        ws.append(list(registro))

    # Generación de nombre único para el archivo
    fecha_actual = datetime.now().strftime('%d-%m-%y')
    documentos_path = os.path.join(os.path.expanduser('~'), 'Documents')
    nombre_archivo = os.path.join(documentos_path, f'informe {fecha_actual}.xlsx')

    # Manejo de nombres duplicados
    contador = 1
    while os.path.exists(nombre_archivo):
        nombre_archivo = os.path.join(documentos_path, f'informe {fecha_actual} ({contador}).xlsx')
        contador += 1

    # Intento de guardado del archivo
    try:
        wb.save(nombre_archivo)
        return jsonify({
            "status": "success", 
            "message": f"Reporte creado exitosamente en la carpeta 'Documentos'."
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error al crear el reporte: {str(e)}"
        })