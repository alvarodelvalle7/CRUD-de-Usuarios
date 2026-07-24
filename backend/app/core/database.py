from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.settings import settings

# Administra las conexiones a la base de datos
# Le pasamos la URL de la base de datos y echo=True hace que SQLAlchemy muestre por consola todas las consultas SQL que ejecuta
engine = create_engine(settings.database_url, echo=settings.debug)

# Clase base de la que heredarán todos los modelos de SQLAlchemy.
# Gracias a ella, SQLAlchemy los reconocerá como tablas de la base de datos.
class Base(DeclarativeBase):
    pass

# sessionmaker no crea una sesión inmediatamente, sino que prepara cómo deben crearse.
# después se hace db = SessionLocal() y ahí sí se crea una nueva sesión para trabajar con la base de datos
SessionLocal = sessionmaker(
    bind=engine, # quiere decir que todas las sesiones se conectarán a la misma base de datos.
    autoflush=False, # Evita que SQLAlchemy sincronice automáticamente los cambios pendientes con la base de datos antes de ejecutar una consulta.
    autocommit=False # Los cambios solo se guardarán cuando se llame a db.commit().
)

# Crea una sesión con la base de datos, la entrega a FastAPI y la cierra automáticamente al finalizar la petición.
def get_db():
    
    # Crea una nueva sesión para interactuar con la base de datos.
    db: Session = SessionLocal()

    try:
        # yield entrega la sesión a FastAPI y pausa la función hasta que termina la petición.
        # Con return, la función terminaría y nunca se ejecutaría el bloque finally.
        yield db
    except:
        db.rollback()
        raise
    finally: # Se ejecuta siempre al finalizar la petición.
        # Cierra la sesión y libera la conexión con la base de datos para no consumir recursos innecesariamente.
        db.close()
