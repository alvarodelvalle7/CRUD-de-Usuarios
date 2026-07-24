# BACKEND CRUD
---

Este documento recoge, en orden, los pasos seguidos para construir este proyecto (una API CRUD de usuarios con FastAPI, capas separadas, PostgreSQL, tests y Docker). Sirve como referencia para poder repetir el mismo proceso en otros proyectos.

## 1. Instalación del proyecto

1. `uv venv` -> Crea un entorno virtual.
2. `.venv\Scripts\Activate.ps1` -> Inicializa el entorno virtual.
3. `Get-Command python` -> Para revisar que el entorno virtual está activo.
4. `uv add "fastapi[standard]"` -> Instala FastAPI y sus dependencias.

## 2. Primer endpoint con FastAPI

Creamos `app/main.py` con lo mínimo para comprobar que el servidor responde:

```python
from fastapi import FastAPI

# Crea una instancia de FastAPI. La variable `app` representa la aplicación
# y será el objeto principal para definir rutas y configurar la API.
app = FastAPI()

# Define una ruta GET para el path "/".
# Cuando un cliente acceda a "/", se ejecutará la función `root()`.
@app.get("/")
async def root():
    return {"message": "Hello world!"}
```

`fastapi dev` -> Ejecuta el servidor en modo desarrollo (con recarga automática) para comprobar que el endpoint funciona.

## 3. Dependencias del proyecto (`pyproject.toml`)

Usamos `uv` como gestor de paquetes en vez de `pip` + `requirements.txt`. Todas las dependencias reales del proyecto quedan fijadas aquí (y en `uv.lock`):

```toml
[project]
name = "todoapp"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "alembic>=1.18.5",
    "fastapi[standard]>=0.139.2",
    "psycopg[binary]>=3.3.4",
    "pydantic-settings>=2.14.2",
    "sqlalchemy>=2.0.51",
]

[tool.fastapi]
entrypoint = "main:app"

[dependency-groups]
dev = [
    "httpx>=0.28.1",
    "pytest>=9.1.1",
    "pytest-asyncio>=1.4.0",
    "pytest-cov>=7.1.0",
]
```

- **`dependencies`** -> lo que necesita la app para funcionar en producción.
- **`dependency-groups.dev`** -> lo que solo hace falta para desarrollar y testear (no se instala en producción).
- `uv add <paquete>` añade una dependencia nueva; `uv add --dev <paquete>` la añade solo al grupo de desarrollo.

## 4. Parámetro de PATH (repaso rápido de FastAPI)

```python
# Parámetro de path: {item_id} cambia según lo que envíe el cliente en la URL.
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

## 5. Configuración (`app/core/settings.py`)

Centraliza toda la configuración de la app, leída automáticamente desde variables de entorno (o un archivo `.env` en desarrollo):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

# Clase que hereda de BaseSettings para cargar automáticamente
# la configuración desde variables de entorno (.env)
class Settings(BaseSettings):

    # URL de conexión a la base de datos
    database_url: str
    # Variable para el nombre de la app
    app_name: str
    # Variable para poder ver las consultas SQL
    debug: bool
    # Variable que permite acceder al frontend
    allowed_origins: list[str]

    # Guarda la instancia de SettingsConfigDict (sirve en este caso para señalar qué archivo leer '.env' y en qué formato 'utf-8')
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# Instancia única de la configuración para reutilizarla en toda la aplicación
settings = Settings()
```

**Por qué:** todos los campos son obligatorios (sin valor por defecto) a propósito — así la app nunca arranca con configuración incompleta a medias. Cuando una variable como `allowed_origins` es una lista, hay que escribirla en el `.env` como JSON: `ALLOWED_ORIGINS=["http://localhost:4200"]`.

## 6. Conexión a la base de datos (`app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.settings import settings

# Administra las conexiones a la base de datos.
# echo=settings.debug hace que SQLAlchemy muestre por consola todas las consultas SQL que ejecuta.
engine = create_engine(settings.database_url, echo=settings.debug)

# Clase base de la que heredarán todos los modelos de SQLAlchemy.
class Base(DeclarativeBase):
    pass

# sessionmaker no crea una sesión inmediatamente, sino que prepara cómo deben crearse.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # Evita que SQLAlchemy sincronice cambios pendientes antes de cada consulta.
    autocommit=False, # Los cambios solo se guardan cuando se llama a db.commit().
)

# Crea una sesión con la base de datos, la entrega a FastAPI y la cierra automáticamente al finalizar la petición.
def get_db():
    db: Session = SessionLocal()
    try:
        yield db  # Entrega la sesión y pausa la función hasta que termina la petición.
    except:
        db.rollback()
        raise
    finally:  # Se ejecuta siempre al finalizar la petición.
        db.close()
```

**Nota:** las tablas **no** se crean con `Base.metadata.create_all()` — se gestionan con migraciones de Alembic (ver punto 12). Esto evita el problema de tener un esquema que "funciona por casualidad" en vez de estar controlado por un historial de migraciones.

## 7. Schemas de Pydantic (`app/schemas/user.py`)

Definen qué datos entran y salen de la API, con sus validaciones:

```python
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Nombre del Usuario", examples=["Álvaro"])
    age: int = Field(..., ge=18, description="Edad del Usuario", examples=[30])
    height: float = Field(..., gt=0, description="Altura del Usuario", examples=[1.92])
    weight: float = Field(..., gt=0, description="Peso del Usuario", examples=[95.1])
    city: Optional[str] = Field(default=None, description="Ciudad de Nacimiento del Usuario", examples=["Zaragoza"])
    is_admin: bool = Field(..., description="Tipo de Usuario", examples=[False])

    # Permite que Pydantic lea los atributos de un objeto (ej. un modelo de SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
```

- **`UserCreate`/`UserUpdate`** -> lo que puede enviar el cliente.
- **`UserResponse`** -> lo que devuelve la API (añade `id`).
- **`from_attributes=True`** -> permite construir estos schemas directamente a partir de un objeto `User` de SQLAlchemy, sin convertirlo antes a diccionario.

## 8. Modelo de la tabla (`app/models/user.py`)

```python
from typing import Optional
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
```

> ⚠️ **Importante** -> Si una clase no hereda de `Base`, será una clase normal de Python, no una tabla.

`app/models/__init__.py` importa `User` explícitamente (`from .user import User`) para que Alembic (y `Base.metadata`) sepa que este modelo existe, aunque en el código no se use ese import directamente.

## 9. Excepciones personalizadas (`app/exceptions/`)

Para no mezclar errores de negocio con errores técnicos de Python:

```python
# app/exceptions/user_exceptions.py
class UserNotFoundException(Exception):
    pass
```

```python
# app/exceptions/database_exceptions.py
class DatabaseException(Exception):
    pass
```

Y sus manejadores, que convierten esas excepciones en respuestas HTTP con el formato adecuado:

```python
# app/exceptions/exception_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import UserNotFoundException

async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
```

**Por qué:** el repositorio y el servicio lanzan estas excepciones "de negocio" en vez de dejar que suba un error crudo de SQLAlchemy o un `None` silencioso. FastAPI las intercepta gracias a `setup_exception_handlers(app)` y las convierte en un JSON con el código HTTP correcto.

## 10. Repositorio (`app/repositores/user_repository.py`)

Es la única capa que toca la base de datos directamente. Hace los métodos CRUD:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.database_exceptions import DatabaseException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        # model_dump() convierte el schema de Pydantic en un diccionario,
        # ** lo desempaqueta en parámetros y User(...) crea el modelo de SQLAlchemy.
        user_model = User(**user.model_dump())
        try:
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)  # Vuelve a leer el usuario para obtener su estado actualizado.
            return user_model
        except Exception as e:
            self.db.rollback()
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_users(self) -> list[User]:
        return self.db.scalars(select(User)).all()

    def update_user(self, user_id: int, user: UserUpdate) -> User | None:
        user_model = self.db.get(User, user_id)
        if user_model is None:
            return None

        for key, value in user.model_dump().items():
            setattr(user_model, key, value)

        try:
            self.db.commit()
            self.db.refresh(user_model)
            return user_model
        except Exception as e:
            self.db.rollback()
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e

    def delete_user_by_id(self, user_id: int) -> User | None:
        user_model = self.db.get(User, user_id)
        if user_model is None:
            return None

        try:
            self.db.delete(user_model)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e

        return user_model
```

**Por qué el `try/except` con `rollback()`:** si algo falla al escribir en la base de datos, hay que deshacer los cambios a medias (`rollback`) antes de avisar del error (`DatabaseException`), para no dejar la sesión en un estado inconsistente.

## 11. Servicio (`app/services/user_service.py`)

Aplica las reglas de negocio que no puede validar un `Schema` (por ejemplo, "el usuario debe existir"):

```python
from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserNotFoundException
from app.models.user import User
from app.repositores.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

class UserService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, user: UserCreate) -> User:
        return self.repository.create_user(user)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        return user

    def get_users(self) -> list[User]:
        return self.repository.get_users()

    def update_user(self, user: UserUpdate, user_id: int) -> User:
        updated_user = self.repository.update_user(user, user_id)
        if updated_user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        return updated_user

    def delete_user_by_id(self, user_id: int) -> User:
        deleted_user = self.repository.delete_user_by_id(user_id)
        if deleted_user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        return deleted_user
```

**Capas y responsabilidades, resumido:** `Router` (HTTP) → `Service` (reglas de negocio) → `Repository` (acceso a datos) → `Model` (tabla). Cada capa solo conoce la de justo debajo.

## 12. Endpoints (`app/routers/user_router.py`)

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    return UserService(db).create_user(user)

@router.get("/", response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]) -> list[UserResponse]:
    return UserService(db).get_users()

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    return UserService(db).get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    return UserService(db).update_user(user_id, user)

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    return UserService(db).delete_user_by_id(user_id)
```

`Depends(get_db)` -> FastAPI llama a `get_db()` antes de ejecutar el endpoint, le entrega la sesión de base de datos, y la cierra automáticamente al terminar (esté o no esté todo bien).

## 13. Middlewares personalizados (`app/middlewares/`)

Código que se ejecuta en **todas** las peticiones, antes y/o después del endpoint:

- **`request_id.py`** -> genera un identificador único por petición (`X-Request-ID`), útil para rastrear una petición concreta en los logs.
- **`process_time.py`** -> mide cuánto tarda la petición y lo añade como cabecera `X-Process-Time`.
- **`logging.py`** -> registra método, ruta, código de estado y duración de cada petición.
- **`security_headers.py`** -> añade cabeceras de seguridad básicas (`X-Frame-Options`, `X-Content-Type-Options`).

Ejemplo (`process_time.py`):

```python
import time
from fastapi import Request

async def process_time_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)         # Deja pasar la petición hacia el router
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 14. Aplicación principal (`app/main.py`)

Aquí se junta todo: middlewares, router y manejadores de excepciones:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.settings import settings
from app.exceptions.exception_handlers import setup_exception_handlers
from app.middlewares.logging import logging_middleware
from app.middlewares.process_time import process_time_middleware
from app.middlewares.request_id import request_id_middleware
from app.middlewares.security_headers import security_headers_middleware
from app.routers import user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Todo lo que esté antes de 'yield' se ejecuta al arrancar; después, al cerrar.
    yield

app = FastAPI(
    title="CRUD de Usuarios",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(process_time_middleware)
app.middleware("http")(request_id_middleware)
app.middleware("http")(logging_middleware)
app.middleware("http")(security_headers_middleware)

app.include_router(user_router.router, prefix="/api/v1", tags=["Users"])
setup_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Ruta '/' funcionando correctamente."}
```

## 15. Migraciones con Alembic

### Instalación e inicialización

1. `uv add alembic` -> Instala la dependencia.
2. `uv run alembic init alembic` -> Crea la carpeta `alembic/` desde la raíz del proyecto.

### Archivos de Alembic

- **`alembic.ini`** -> configuración general (ruta de las migraciones, logs).
- **`alembic/env.py`** -> el puente entre Alembic y la app: le dice de dónde sacar el `engine` y la `metadata` de los modelos.
- **`alembic/versions/`** -> aquí viven las migraciones generadas.

`alembic/env.py` reutiliza el mismo `engine` que usa la app, así que se conecta siempre a la misma base de datos que define `DATABASE_URL`:

```python
from alembic import context
import app.models
from app.core.database import Base, engine

target_metadata = Base.metadata

def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### Generar y aplicar una migración

1. Modificar el modelo (`app/models/user.py`).
2. `uv run alembic revision --autogenerate -m "mensaje descriptivo"` -> genera el archivo de migración; **revisar siempre** el archivo generado antes de aplicarlo.
3. `uv run alembic upgrade head` -> aplica las migraciones pendientes.

> ⚠️ **Importante** -> Si `autogenerate` no detecta ninguna diferencia (por ejemplo, porque la tabla ya existía en la base de datos por otra vía), genera una migración con `upgrade()`/`downgrade()` vacíos (`pass`). Esa migración no sirve para crear nada en una base de datos nueva — hay que revisar siempre el contenido generado, no solo confiar en que "no dio ningún error".

## 16. Tests (`tests/`)

El proyecto usa `pytest`, con una base de datos SQLite en memoria completamente aislada de la base de datos real, para que los tests sean rápidos, repetibles y no dependan de tener Postgres levantado.

### Estructura

```
tests/
├── conftest.py              # fixtures compartidas: db_session, client
├── helpers.py                # fábricas de datos de prueba (make_fake_user, etc.)
├── test_root.py               # test de la ruta "/"
├── test_user_service.py       # unitarios, con el repositorio "mockeado"
├── test_user_repository.py    # integración, contra la BD de prueba real
└── test_user.py                # end-to-end, contra los endpoints HTTP
```

### `conftest.py` — la base de datos de prueba y el cliente HTTP

```python
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Permite conexiones desde otro hilo
    poolclass=StaticPool,                          # Permite que los datos persistan dentro de un mismo test
)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Crea las tablas, entrega una sesión y, al terminar el test, las destruye.
# Así cada test empieza siempre con una base de datos limpia.
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

# Sustituye get_db por la sesión de prueba, para que los endpoints no toquen la BD real.
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Los tres niveles de test

1. **`test_user_service.py` (unitarios)** -> mockea `UserRepository` con `unittest.mock.patch`, para probar solo las reglas de negocio (por ejemplo, que `get_user_by_id` lance `UserNotFoundException` si el repositorio devuelve `None`), sin tocar ninguna base de datos.
2. **`test_user_repository.py` (integración)** -> usa la fixture `db_session` de verdad, para comprobar que el SQL generado por SQLAlchemy funciona (crear, leer, actualizar, borrar).
3. **`test_user.py` (end-to-end)** -> usa la fixture `client` para hacer peticiones HTTP reales contra los endpoints, comprobando el contrato completo de la API (`response.status_code`, `response.json()`).

`@pytest.mark.parametrize` se usa para probar varias validaciones de Pydantic (edad mínima, longitud del nombre...) con un solo test, en vez de repetirlo para cada caso.

### Ejecutar los tests

```powershell
uv run pytest                                    # Ejecuta todos los tests
uv run pytest --cov=app --cov-report=term-missing  # Con cobertura, mostrando líneas sin cubrir
```

## 17. Docker

El proyecto está preparado para ejecutarse en contenedores: backend (FastAPI) + base de datos (PostgreSQL), unidos con Docker Compose. El proceso completo, con los problemas encontrados y cómo se resolvieron, está documentado en detalle en **`DOCKER-ROADMAP.MD`**; aquí queda el resumen limpio de la versión final.

### `.dockerignore`

Evita copiar a la imagen archivos innecesarios o con información sensible:

```
.venv/
__pycache__/
**/__pycache__/
.pytest_cache/
.env
*.pyc
```

### `Dockerfile`

```dockerfile
# 1. Imagen que trae Python 3.13 instalado y funcionando
FROM python:3.13-slim

# 2. Traemos uv ya listo, sin tener que instalarlo con pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos solo la lista de dependencias e instalamos lo que necesita el proyecto
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# 5. Copiamos el resto del proyecto y terminamos de instalar
COPY . .
RUN uv sync --locked

# 6. Le decimos al contenedor dónde están los programas ya instalados (python, fastapi...)
ENV PATH="/app/.venv/bin:$PATH"

# 7. La app escucha en el puerto 8000
EXPOSE 8000

# 8. Comando que arranca la app cada vez que se enciende el contenedor
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

**Por qué en ese orden:** copiar primero `pyproject.toml`/`uv.lock` e instalar dependencias, y copiar el resto del código después, permite que Docker reutilice la capa de dependencias (que cambia poco) cuando solo se modifica el código (que cambia mucho) — reconstruir la imagen es mucho más rápido.

> ⚠️ **Importante** -> Una imagen es una foto fija del proyecto en el momento de construirla (`docker build`). Editar archivos después no la actualiza — hay que reconstruirla (`docker compose up -d --build`) para que los cambios se reflejen dentro del contenedor.

### Variables de entorno

Las 4 variables que pide `settings.py` (`DATABASE_URL`, `APP_NAME`, `DEBUG`, `ALLOWED_ORIGINS`) se cargan desde el `.env` real del proyecto (nunca copiado dentro de la imagen), y solo `DATABASE_URL` se sobreescribe para apuntar al contenedor de la base de datos en vez de a `localhost`.

### `compose.yaml`

Une el backend y la base de datos, crea la red y el volumen automáticamente, y evita tener que escribir `docker network create` / `docker run` a mano:

```yaml
services:
  db:
    image: postgres:17
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: caialvaro7
      POSTGRES_DB: crud_user_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    depends_on:
      - db
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:caialvaro7@db:5432/crud_user_db
    ports:
      - "8000:8000"

volumes:
  pgdata:
```

### Comandos esenciales

```powershell
docker compose up -d --build              # Construye (si hace falta) y levanta backend + db juntos
docker compose run --rm backend alembic upgrade head   # Aplica las migraciones dentro del contenedor
docker compose logs -f backend             # Ver logs de un servicio en concreto
docker compose down                        # Para y borra los contenedores (el volumen pgdata NO se borra)
```

### Desarrollo vs producción

El `Dockerfile` actual está pensado para **producción**: usa `fastapi run` (sin recarga automática) y el código se copia una sola vez, al construir la imagen. Para programar día a día, se sigue usando `uv run fastapi dev` en local (conectando, si se quiere, contra el Postgres que corre en Docker) — y se usa `docker compose up -d --build` solo para comprobar que "el paquete final" funciona de verdad antes de dar algo por terminado.
