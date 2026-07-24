# conftest es un archivo especial que pytest busca automáticamente. Es el lugar donde se configura el entorno de pruebas.
# Para ejecutar -> uv run pytest

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from sqlalchemy.pool import StaticPool

# Variable de entorno para la URL de la base de datos de prueba
TEST_DATABASE_URL="sqlite:///:memory:"

# Administra la conexión con la BD de prueba SQLite
engine = create_engine(
    # Se conecta a la base de datos de prueba SQLite
    TEST_DATABASE_URL,
    # Permite hacer conexiones a la BD desde otro hilo
    connect_args={"check_same_thread": False},
    # Permite que los datos persistan dentro de un test
    poolclass=StaticPool,
)

# Variable reutilizable para preparar como debe crearse la BD de prueba de SQlite
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Función fixture para la sesion de la BD
# Crea las tablas, entrega una sesion y al terminar el test las destruye
# Permite que cada test empieza con una BD limpia.
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine) # Crea las tablas
    
    session = TestingSessionLocal()
    
    try:
        yield session # Se ejecuta el test
    finally:
        session.close() # Se cierra la sesión
        Base.metadata.drop_all(bind=engine) # Limpia la base de datos
        
# Función fixture que recibe la fixture de db_session para crear las tablas y da la sesión de SQLAlchemy        
@pytest.fixture
def client(db_session):
    
    # Función anidada que en vez de recoger la BD real, la sustituye por una de prueba
    def override_get_db():
        yield db_session

    # Indica que se use esta función para hacer test en vez de la BD real
    app.dependency_overrides[get_db] = override_get_db
    
    # Abre el cliente de pruebas (simula peticiones HTTP sin levantar un servidor real)
    # y entrega ese cliente al test para que haga sus peticiones (GET, POST, etc.)
    with TestClient(app) as test_client:
        yield test_client # Aquí se ejecuta el test, usando este cliente

    # Cuando el test termina, se quita la sustitución de la BD real
    # para que el siguiente test empiece de cero y no herede este override
    app.dependency_overrides.clear()
     