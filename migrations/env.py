# Importación de módulos necesarios para la configuración y ejecución de migraciones
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app import create_app, db  # Importa la aplicación Flask y la instancia de la base de datos
from app.models.historial import Historial  # Importa el modelo 'Historial'
from app.models.usuario import Usuario  # Importa el modelo 'Usuario'
from app.models.facultad import Facultad  # Importa el modelo 'Facultad'
from app.models.equipo import Equipo  # Importa el modelo 'Equipo'

# Configuración de Alembic
config = context.config  # Obtiene la configuración de Alembic desde el archivo .ini de la migración

# Configuración de archivo de logs
if config.config_file_name is not None:  
    fileConfig(config.config_file_name)  # Si el archivo de configuración está presente, lo carga para los logs

# Establecer los metadatos de los modelos de SQLAlchemy
target_metadata = db.metadata  # Se obtienen los metadatos de la instancia de la base de datos de SQLAlchemy de la app Flask

def run_migrations_offline() -> None:
    """Correr migraciones en modo 'offline'."""
    
    url = config.get_main_option("sqlalchemy.url")  # Se obtiene la URL de la base de datos desde la configuración de Alembic
    context.configure(
        url=url,  # Se configura la URL para la conexión a la base de datos
        target_metadata=target_metadata,  # Se indican los metadatos para las migraciones
        literal_binds=True,  # Habilita la generación de binds literales (prevenir inyecciones SQL)
        dialect_opts={"paramstyle": "named"},  # Configura el estilo de los parámetros de SQL
    )

    # Inicia la transacción de migración
    with context.begin_transaction():
        context.run_migrations()  # Ejecuta las migraciones definidas

def run_migrations_online() -> None:
    """Correr migraciones en modo 'online'."""
    
    # Se crea un motor de base de datos usando la configuración de Alembic
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),  # Obtiene la sección de configuración de la base de datos
        prefix="sqlalchemy.",  # Prefijo utilizado para identificar las opciones de SQLAlchemy
        poolclass=pool.NullPool,  # Utiliza un pool de conexiones sin almacenamiento
    )

    # Se establece una conexión a la base de datos
    with connectable.connect() as connection:
        context.configure(
            connection=connection,  # Se pasa la conexión activa a Alembic
            target_metadata=target_metadata  # Se configuran los metadatos para las migraciones
        )

        # Inicia la transacción de migración
        with context.begin_transaction():
            context.run_migrations()  # Ejecuta las migraciones definidas

# Verifica si está en modo offline u online
if context.is_offline_mode():
    run_migrations_offline()  # Ejecuta migraciones en modo offline
else:
    run_migrations_online()  # Ejecuta migraciones en modo online
