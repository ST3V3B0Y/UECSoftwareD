# Importación de bibliotecas necesarias para la configuración y funcionalidad de la app
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
from app import create_app, db  # Importa la aplicación y la instancia de la base de datos
from app.models import Equipo  # Importa el modelo 'Equipo'
from app.routes import equipo_routes  # Importa las rutas de equipo si se utilizan
from app.models import Usuario  # Importa el modelo 'Usuario'
from app.models import Facultad  # Importa el modelo 'Facultad'
from app.models import Software  # Importa el modelo 'Software'
from app.config import SERVER_HOST, SERVER_PORT  # Importa la configuración del servidor
import os  # Usado para obtener variables de entorno
import socket  # Para obtener información del socket si es necesario
import threading  # Usado para el manejo de hilos si se necesita
import json  # Usado para procesar datos en formato JSON
import ctypes  # Para interacción con bibliotecas C
import signal  # Para manejar señales de sistema
app = create_app()  # Inicializa la aplicación Flask usando la función `create_app()`

@app.route("/")  # Define la ruta principal del sitio web
def index():
<<<<<<< HEAD
    contraseña = "STU1e3c0"  # Contraseña predefinida para el administrador

    # Registrar un administrador si no existe en la base de datos
    administrador_existente = Usuario.query.filter_by(idUsuario=1).first()
=======
    contraseña ="STU1e3c0"
    #registrar administrador
    administrador_existente = Usuario.query.filter_by(idUsuario=1001).first()
>>>>>>> a4f6a7524caa719de6825a0e960d8644c2967459

    if not administrador_existente:
        administrador = Usuario(
            idUsuario=1001,
            usuario="administrador",
            contraseña=contraseña,
            nombreUsuario="administrador",
            identificacionUsuario="1",
            Facultad_idFacultad=20  # Asocia al administrador con una facultad específica
        )
        try:
            db.session.add(administrador)  # Agrega al administrador a la sesión
            db.session.commit()  # Realiza el commit de los cambios en la base de datos
        except IntegrityError as e:  # Maneja los errores de integridad
            db.session.rollback()  # Revierte la transacción en caso de error
            print("Error registrando administrador", e)

    # Lista de facultades a registrar
    facultades_list = [
        "ADMINISTRACION DE EMPRESAS", "CIENCIA DE DATOS", "MATEMATICAS", 
        "ADMINISTRACION DE EMPRESAS HOTELERAS", "COMUNICACION SOCIAL Y PERIODISMO", 
        "ECONOMIA", "FILOSOFIA", "GEOGRAFIA", "GOBIERNO Y RELACIONES INTERNACIONALES", 
        "HISTORIA", "PSICOLOGIA", "SOCIOLOGIA", "TRABAJO SOCIAL", "ANTROPOLOGIA", 
        "ARQUEOLOGIA", "CONTADURIA PUBLICA", "DERECHO", "FIGRI", "DOCENTE", "ADMINISTRATIVO"
    ]

    # Registra las facultades si no existen
    for facultad in facultades_list:
        facultad_existente = Facultad.query.filter_by(nombreFacultad=facultad).first()
        if not facultad_existente:
            facultad = Facultad(nombreFacultad=facultad)
            try:
                db.session.add(facultad)  # Agrega la facultad a la sesión
                db.session.commit()  # Realiza el commit
            except IntegrityError as e:
                db.session.rollback()  # Revierte la transacción en caso de error
                print(f"Error registrando la facultad {facultad}", e)

    # Lista de software a registrar
    software_list = ["ADOBE CC", "SPSS", "ARCGIS", "RISK SIMULATOR", "STATA", "EVIEWS", "NVIVO"]

    # Registra el software si no existe
    for nombre in software_list:
        software_existente = Software.query.filter_by(nombreSoftware=nombre).first()
        if not software_existente:
            nuevo_software = Software(nombreSoftware=nombre)
            try:
                db.session.add(nuevo_software)  # Agrega el software a la sesión
                db.session.commit()  # Realiza el commit
            except IntegrityError as e:
                db.session.rollback()  # Revierte la transacción en caso de error
                print(f"Error registrando el software {nombre}", e)

    # Asegura que el software "OTRO" existe
    software = Software.query.filter_by(idSoftware=200).first()
    if not software:
        otroSoftware = db.session.execute(text('INSERT INTO Software (idSoftware, nombreSoftware) VALUES (200, :software)'), {'software': "OTRO"})
        db.session.commit()

    # Registrar los equipos de las salas automáticamente
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
                db.session.add(nuevo_equipo)  # Agrega el equipo a la sesión
                db.session.commit()  # Realiza el commit
            except IntegrityError as e:
                db.session.rollback()  # Revierte la transacción en caso de error
                print(f"Error registrando el equipo {i} en sala D507", e)

    # Registra equipos en otras salas (H405, I408) siguiendo el mismo patrón
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

    return render_template('index.html')  # Renderiza la página principal

# Establece el contexto de la aplicación y crea las tablas si no existen
with app.app_context():
    Base = declarative_base()
    target_metadata = db.metadata
    db.create_all()  # Crea todas las tablas definidas en los modelos

# Ejecuta la aplicación en el host y puerto especificados
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=int(os.environ.get('PORT', 5000)))
