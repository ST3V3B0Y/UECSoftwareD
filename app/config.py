# config.py - Archivo de configuración para la aplicación Flask

import os
import secrets

# Configuración de seguridad
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
"""
Clave secreta para la aplicación Flask.
- Primero intenta obtenerla de las variables de entorno (para producción)
- Si no existe, genera una clave aleatoria de 32 bytes (para desarrollo)
Esta clave se usa para:
- Proteger las sesiones de usuario
- Firmar tokens de seguridad
- Prevenir ataques CSRF
"""

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/Disponibilidad_Equipos'
"""
URI de conexión a la base de datos MySQL usando PyMySQL.
Formato: mysql+pymysql://usuario:contraseña@host:puerto/nombre_bd
En este caso:
- Usuario: root
- Sin contraseña (no recomendado para producción)
- Host: localhost
- Puerto: 3306 (puerto default MySQL)
- Nombre BD: Disponibilidad_Equipos
"""

SQLALCHEMY_TRACK_MODIFICATIONS = False
"""
Configuración para optimizar SQLAlchemy:
- False: Desactiva el seguimiento de modificaciones para mejorar performance
- Evita señales innecesarias que podrían ralentizar la aplicación
"""

# Configuración del servidor (opciones comentadas)
# SERVER_HOST = '10.100.103.142'  # Dirección IP alternativa 1
SERVER_HOST = '10.33.0.93'        # Dirección IP principal del servidor
"""
Dirección IP donde el servidor escuchará conexiones.
Usada para:
- Configurar el host del servidor Flask
- Definir dónde estará accesible la aplicación
"""

# SERVER_PORT = 5040              # Puerto alternativo 1
SERVER_PORT = 10000               # Puerto principal del servidor
"""
Puerto TCP donde el servidor escuchará conexiones.
Importante para:
- Acceso a la aplicación (http://host:puerto)
- Configuración de firewalls y red
"""

# Configuración local (desarrollo, comentada)
# SERVER_HOST = 'localhost'      # Host local para desarrollo
# SERVER_PORT = '5000'           # Puerto default Flask para desarrollo
"""
Configuración alternativa para desarrollo local:
- localhost: dirección loopback
- 5000: puerto tradicional para desarrollo Flask
"""