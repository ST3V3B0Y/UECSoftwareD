# Importación de módulos necesarios
from flask import Flask, render_template, Blueprint
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import (
    login_required,
    login_manager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app import create_app, db
from app.models import Equipo
from app.routes import equipo_routes
from app.models import Usuario
from app.models import Facultad
from app.models import Software
from app.config import SERVER_HOST, SERVER_PORT
import os
import socket
import threading
import json
import ctypes
import signal

# Creación de la aplicación Flask
app = create_app()

@app.route("/")
def index():
    """
    Ruta principal de la aplicación que realiza varias tareas de inicialización:
    - Registra un usuario administrador por defecto
    - Carga facultades predefinidas
    - Carga software predefinido
    - Registra equipos de salas específicas
    """
    
    # Contraseña por defecto para el administrador
    contraseña = "STU1e3c0"
    
    # Registro del usuario administrador si no existe
    administrador_existente = Usuario.query.filter_by(idUsuario=1001).first()

    if not administrador_existente:
        administrador = Usuario(
            idUsuario=1001,
            usuario="administrador",
            contraseña=contraseña,
            nombreUsuario="administrador",
            identificacionUsuario="1",
            Facultad_idFacultad=20  # ID de facultad por defecto
        )
        try:
            db.session.add(administrador)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            print("Error registrando administrador", e)

    # Lista de facultades a registrar
    facultades_list = [
        "ADMINISTRACION DE EMPRESAS", "CIENCIA DE DATOS", "MATEMATICAS",
        "ADMINISTRACION DE EMPRESAS HOTELERAS", "COMUNICACION SOCIAL Y PERIODISMO",
        "ECONOMIA", "FILOSOFIA", "GEOGRAFIA", "GOBIERNO Y RELACIONES INTERNACIONALES",
        "HISTORIA", "PSICOLOGIA", "SOCIOLOGIA", "TRABAJO SOCIAL", "ANTROPOLOGIA",
        "ARQUEOLOGIA", "CONTADURIA PUBLICA", "DERECHO", "FIGRI", "DOCENTE", "ADMINISTRATIVO"
    ]
    
    # Registro de facultades si no existen
    for facultad in facultades_list:
        facultad_existente = Facultad.query.filter_by(nombreFacultad=facultad).first()
        if not facultad_existente:
            facultad = Facultad(nombreFacultad=facultad)
            try:
                db.session.add(facultad)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error registrando la facultad {facultad}", e)

    # Lista de software a registrar
    software_list = ["ADOBE CC", "SPSS", "ARCGIS", "RISK SIMULATOR", "STATA", "EVIEWS", "NVIVO"]

    # Registro de software si no existe
    for nombre in software_list:
        software_existente = Software.query.filter_by(nombreSoftware=nombre).first()
        if not software_existente:
            nuevo_software = Software(nombreSoftware=nombre)
            try:
                db.session.add(nuevo_software)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error registrando el software {nombre}", e)
    
    # Registro especial para software "OTRO"
    software = Software.query.filter_by(idSoftware=200).first()
    if not software:
        otroSoftware = db.session.execute(
            text('INSERT INTO Software (idSoftware, nombreSoftware) VALUES (200, :software)'),
            {'software': "OTRO"}
        )
        db.session.commit()

    # Registro automático de equipos en diferentes salas
    
    # Sala D507 (equipos 1-68)
    for i in range(1, 69):
        equipo_existente = Equipo.query.filter_by(idEquipo=i, sala="D507").first()
        if not equipo_existente:
            nuevo_equipo = Equipo(
                idEquipo=i,
                estadoEquipo="libre",
                sala="D507",
                ipEquipo=0
            )
            try:
                db.session.add(nuevo_equipo)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error registrando el equipo {i} en sala D507", e)

    # Sala H405 (equipos 101-134)
    for i in range(101, 135):
        equipo_existente = Equipo.query.filter_by(idEquipo=i, sala="H405").first()
        if not equipo_existente:
            nuevo_equipo = Equipo(
                idEquipo=i,
                estadoEquipo="libre",
                sala="H405",
                ipEquipo=0
            )
            try:
                db.session.add(nuevo_equipo)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print(f"Error registrando el equipo {i} en sala H405")

    # Sala I408 (equipos 201-224)
    for i in range(201, 225):
        equipo_existente = Equipo.query.filter_by(idEquipo=i, sala="I408").first()
        if not equipo_existente:
            nuevo_equipo = Equipo(
                idEquipo=i,
                estadoEquipo="libre",
                sala="I408",
                ipEquipo=0
            )
            try:
                db.session.add(nuevo_equipo)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print(f"Error registrando el equipo {i} en sala I408")

    return render_template('index.html')

# Configuración de la base de datos
with app.app_context():
    Base = declarative_base()
    target_metadata = db.metadata
    db.create_all()  # Crea todas las tablas definidas en los modelos

# Punto de entrada principal
if __name__ == '__main__':
    # Inicia el servidor Flask
    app.run(debug=True, host='localhost', port=int(os.environ.get('PORT', 5000)))