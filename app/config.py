# Importa módulos necesarios
import os  # Para interactuar con el sistema operativo y acceder a variables de entorno
import secrets  # Para generar claves secretas de manera segura

# Configuración de la clave secreta de la aplicación
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))  
# Intenta obtener la variable de entorno 'SECRET_KEY'. Si no está definida,
# genera una clave secreta aleatoria de 32 bytes utilizando 'secrets.token_hex'.
# Esta clave se usa para sesiones y protección contra ataques CSRF.

# Configuración de la URI para conectarse a la base de datos
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/Disponibilidad_Equipos'
# Esta es la cadena de conexión para SQLAlchemy, que permite a la aplicación conectarse a la base de datos MySQL.
# Está usando el controlador pymysql para conectarse a un servidor MySQL en 'localhost' en el puerto 3306 y a la base de datos 'Disponibilidad_Equipos'.

# Deshabilita el seguimiento de modificaciones de objetos en la base de datos, lo cual es innecesario y consume recursos
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración del servidor de la aplicación
# Define la IP y el puerto del servidor donde la aplicación Flask se ejecutará.

# SERVER_HOST = '10.100.103.142'  # Comentada, esta línea especificaba una IP diferente para el servidor.
SERVER_HOST = '10.33.0.93'  # Define la IP del servidor donde se ejecutará la aplicación Flask.

# Define el puerto en el que la aplicación Flask escuchará las conexiones entrantes.
SERVER_PORT = 10000  # El puerto de la aplicación, 10000 en este caso.

# SERVER_PORT = 5040  # Comentada, esta línea especificaba un puerto diferente (5040) para el servidor.
# SERVER_HOST = 'localhost'  # Comentada, esta línea especificaba 'localhost' como la dirección del servidor.
# SERVER_PORT = '5000'  # Comentada, especifica el puerto 5000 como el puerto para ejecutar Flask en desarrollo.
