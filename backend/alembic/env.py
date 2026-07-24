from logging.config import fileConfig

from alembic import context
import app.models
from app.core.database import Base, engine

# Se encarga de cargar el archivo alembic.ini
config = context.config

# Configura el sistema de logs de alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Indica a Alembic la metadata de los modelos para que pueda detectar los cambios y generar las migraciones.
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Se encarga de conectarse a la base de datos y ejecutar las migraciones.
def run_migrations_online() -> None:
    """Ejecuta las migraciones conectándose a la base de datos."""

    # Utiliza el mismo Engine que usa la aplicación FastAPI.
    connectable = engine

    # Abre una conexión con la base de datos.
    with connectable.connect() as connection:
        # Configura Alembic con la conexión y la metadata de los modelos.
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Inicia una transacción para aplicar las migraciones de forma segura.
        with context.begin_transaction():
            context.run_migrations() # Ejecuta las migraciones pendientes.


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
