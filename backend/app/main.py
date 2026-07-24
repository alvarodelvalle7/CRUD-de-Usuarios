# Importamos FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.settings import settings
from app.core.database import Base, engine
from app.core.database import Base
from app.exceptions.exception_handlers import setup_exception_handlers
from app.middlewares.logging import logging_middleware
from app.middlewares.process_time import process_time_middleware
from app.middlewares.request_id import request_id_middleware
from app.middlewares.security_headers import security_headers_middleware
from app.routers import user_router

# Función que se ejecuta una sola vez al iniciar y al cerrar la aplicación.
# Todo lo que esté antes de 'yield' se ejecuta al arrancar.
# Todo lo que esté después de 'yield' se ejecuta al cerrar.
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Se ejecuta una sola vez al iniciar la aplicación.

    # Crea automáticamente las tablas que no existan en la base de datos.
    # Si una tabla ya existe, no la modifica ni la vuelve a crear.
    # Recomendado para desarrollo y proyectos pequeños.
    # Base.metadata.create_all(bind=engine) # Ahora las tablas de la base de datos se gestionan mediante migraciones de Alembic.
    
    yield
    
# Crea una instancia de FastAPI. La variable `app` representa la aplicación
# y será el objeto principal para definir rutas y configurar la API.
app = FastAPI(
    title="CRUD de Usuarios",
    description="Proyecto para aprender a utilizar FastAPI con un CRUD de Usuarios.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Añade el middleware CORS, que se ejecutará antes de que la petición llegue a los routers.
# Su función es comprobar si el origen de la petición tiene permiso para acceder a la API.
app.add_middleware(
    CORSMiddleware, # Middleware que comprueba si el origen de la petición tiene permiso para acceder a la API.
    allow_origins=settings.allowed_origins, # Lista de orígenes autorizados para acceder a la API.
    allow_credentials=True, # Permite enviar cookies y cabeceras de autenticación.
    allow_methods=["*"], # Permite utilizar cualquier método HTTP (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"], # Permite enviar cualquier cabecera HTTP (Authorization, Content-Type, etc.).
)

# Middlewares personalizados
app.middleware("http")(process_time_middleware)
app.middleware("http")(request_id_middleware)
app.middleware("http")(logging_middleware)
app.middleware("http")(security_headers_middleware)


# Incluimos el router de usuarios al archivo main.py
app.include_router(user_router.router, prefix="/api/v1", tags=["Users"])

# Añadimos todas las excepciones a nuestro archivo 'main.py'
setup_exception_handlers(app)

# Define una ruta GET para el path "/".
# Cuando un cliente acceda a "/", se ejecutará la función `root()`.
@app.get("/")
async def root():

    # Devuelve el mensaje Hello world! en formato JSON
    return {"message": "Ruta '/' funcionando correctamente."}