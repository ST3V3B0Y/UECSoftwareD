# Importación de módulos necesarios
from flask import Flask  # Flask es el framework principal para la aplicación web
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy para manejar la base de datos
from flask_login import LoginManager  # Extensión para manejar la autenticación de usuarios
import socket  # Protocolo de comunicación de red
import threading  # Para la ejecución de hilos (threads)
import json  # Para manipular datos en formato JSON
import pymysql  # Biblioteca para interactuar con bases de datos MySQL
import time  # Para gestionar tiempos y retardos
from time import sleep  # Importación de sleep para pausar la ejecución

# Inicialización de las extensiones de Flask
db = SQLAlchemy()  # Instancia de SQLAlchemy para gestionar la base de datos
login_manager = LoginManager()  # Instancia de LoginManager para gestionar la autenticación

def create_app():
    """
    Función principal para crear y configurar la aplicación Flask.
    - Configura las extensiones necesarias.
    - Registra las rutas (blueprints).
    - Verifica o crea la base de datos.
    
    Returns:
        app: la aplicación Flask configurada.
    """
    app = Flask(__name__)  # Creación de la instancia de Flask
    app.config.from_pyfile("config.py")  # Carga la configuración desde el archivo "config.py"

    init_extensions(app)  # Inicializa las extensiones como la base de datos y LoginManager
    register_blueprints(app)  # Registra los diferentes blueprints de rutas
    create_database_if_not_exists('disponibilidad_equipos')  # Verifica si la base de datos existe o la crea
    
    return app  # Devuelve la aplicación Flask configurada

def create_database_if_not_exists(db_name):
    """
    Función que verifica si la base de datos existe y la crea si no es así.
    Utiliza MySQL para conectarse y verificar la existencia de la base de datos.
    
    Args:
        db_name (str): El nombre de la base de datos a verificar o crear.
    """
    # Establece la conexión a la base de datos MySQL. Se conecta a localhost en el puerto 3306.
    conn = pymysql.connect(user='root', password='', host='127.0.0.1', port=3306)
    cursor = conn.cursor()  # Crea un cursor para ejecutar las consultas
    
    try:
        # Intenta crear la base de datos si no existe.
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base de datos {db_name} verificada o creada.")  # Mensaje de confirmación
    except Exception as e:
        print("Error al crear base de datos:", e)  # Si hay un error, muestra un mensaje
    
    # Cierra el cursor y la conexión a la base de datos
    cursor.close()
    conn.close()

def init_extensions(app):
    """
    Inicializa las extensiones necesarias para la aplicación Flask.
    Configura la base de datos y el LoginManager.
    
    Args:
        app: La instancia de la aplicación Flask.
    """
    db.init_app(app)  # Inicializa la extensión de base de datos
    login_manager.init_app(app)  # Inicializa la extensión de autenticación de usuarios
    
    # Configuración del LoginManager
    login_manager.login_view = 'usuario.login'  # Ruta a la que se redirige si el usuario no está autenticado
    login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."  # Mensaje mostrado
    login_manager.login_message_category = "info"  # Categoría del mensaje (utilizado para dar estilo en templates)
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Función que carga un usuario a partir de su ID.
        
        Args:
            user_id (int): El ID del usuario que se va a cargar.
        
        Returns:
            Usuario: El objeto del usuario si se encuentra en la base de datos, de lo contrario None.
        """
        from .models.usuario import Usuario  # Importa el modelo de usuario
        return Usuario.query.get(int(user_id))  # Consulta la base de datos para obtener el usuario por su ID

def register_blueprints(app):
    """
    Registra los blueprints (rutas) de la aplicación.
    
    Args:
        app: La instancia de la aplicación Flask.
    """
    # Importa las rutas de diferentes módulos de la aplicación
    from app.routes import (accion_routes, equipo_routes, facultad_routes, historial_routes, usuario_routes, software_routes)
    
    # Registra cada blueprint para que sus rutas estén disponibles en la aplicación
    app.register_blueprint(accion_routes.bp)
    app.register_blueprint(equipo_routes.bp)
    app.register_blueprint(facultad_routes.bp)
    app.register_blueprint(historial_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(software_routes.bp)
