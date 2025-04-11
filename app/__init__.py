# Importación de librerías necesarias
from flask import Flask  # Framework web Flask
from flask_sqlalchemy import SQLAlchemy  # ORM para bases de datos
from flask_login import LoginManager  # Gestión de autenticación de usuarios
import socket  # Para operaciones de red
import threading  # Para ejecución concurrente
import json  # Para manejo de datos JSON
import pymysql  # Conector MySQL para Python
import time  # Para operaciones relacionadas con tiempo
from time import sleep  # Para pausas en la ejecución

# Inicialización de extensiones Flask
db = SQLAlchemy()  # Instancia de SQLAlchemy para la base de datos
login_manager = LoginManager()  # Instancia para manejar la autenticación de usuarios

def create_app():
    """
    Función factory para crear y configurar la aplicación Flask.
    
    Returns:
        Flask: La aplicación Flask configurada
    """
    app = Flask(__name__)  # Creación de la aplicación Flask
    app.config.from_pyfile("config.py")  # Carga de configuración desde archivo config.py

    # Configuración inicial de la aplicación
    init_extensions(app)  # Inicialización de extensiones
    register_blueprints(app)  # Registro de blueprints (rutas)
    create_database_if_not_exists('disponibilidad_equipos')  # Creación de BD si no existe
    
    return app  # Retorna la aplicación configurada

def create_database_if_not_exists(db_name):
    """
    Crea la base de datos si no existe.
    
    Args:
        db_name (str): Nombre de la base de datos a crear/verificar
    """
    # Conexión al servidor MySQL (comentado: versión alternativa con reintento)
    # try:
    #     conn = pymysql.connect(user='root', password='1234', host='localhost', port=8000)
    # except pymysql.OperationalError:
    #     print("Esperando a que Mysql esté listo...")
    #     time.sleep(3)
               
    conn = pymysql.connect(user='root', password='', host='127.0.0.1', port=3306)
    cursor = conn.cursor()
    
    try:
        # Ejecuta el comando SQL para crear la BD si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base de datos {db_name} verificada o creada.")
    except Exception as e:
        print("error al crear database ", e)  # Manejo de errores

    # Cierre de conexión
    cursor.close()
    conn.close()
    
def init_extensions(app):
    """
    Inicializa las extensiones Flask con la aplicación.
    
    Args:
        app (Flask): Aplicación Flask a configurar
    """
    # Configuración de extensiones
    db.init_app(app)  # Inicializa SQLAlchemy con la app
    login_manager.init_app(app)  # Inicializa LoginManager con la app
    
    # Configuración de LoginManager
    login_manager.login_view = 'usuario.login'  # Vista para login
    login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."  # Mensaje de login
    login_manager.login_message_category = "info"  # Categoría del mensaje (para estilos)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback para cargar un usuario basado en su ID.
        
        Args:
            user_id (str): ID del usuario a cargar
            
        Returns:
            Usuario: Objeto usuario correspondiente al ID
        """
        from .models.usuario import Usuario  # Importación local para evitar circular imports
        return Usuario.query.get(int(user_id))  # Consulta el usuario por ID

def register_blueprints(app):
    """
    Registra los blueprints (conjuntos de rutas) en la aplicación Flask.
    
    Args:
        app (Flask): Aplicación Flask donde registrar las rutas
    """
    # Importación de blueprints desde el módulo de rutas
    from app.routes import (accion_routes, equipo_routes, facultad_routes,
                           historial_routes, usuario_routes, software_routes)
    
    # Registro de cada blueprint en la aplicación
    app.register_blueprint(accion_routes.bp)
    app.register_blueprint(equipo_routes.bp)
    app.register_blueprint(facultad_routes.bp)
    app.register_blueprint(historial_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(software_routes.bp)