# ROADMAP DE DOCKER
---
## Creación del archivo ``.dockerignore``

1. Creamos el archivo ejecutando el siguiente comando:

```
New-Item -ItemType File -Path ".dockerignore"
```

2. Después colocamos los archivos y carpetas que no queremos que entren en la imagen de ``Docker``.

```
    # .venv se incluye porque pesa mucho
    .venv/
    # No hace falta copiarlas ya que son versiones compiladas del código
    __pycache__/
    **/__pycache__/
    # No aporta nada a la imagen de producción
    .pytest_cache/
    # Variables reales del proyecto con información confidencial
    .env
    # Por si algún archivo .pyc se ha quedado fuera de una carpeta
    *.pyc
```

## Creación del archivo ``Dockerfile``

1. Creamos el archivo ejecutando el siguiente comando:

```
New-Item -ItemType File -Path "Dockerfile"

```

2. Después colocamos dentro del archivo instrucciones de como construir la imagen del backend.

```
# 1. Imagen que trae Python 3.13 instalado y funcionando
# slim le dice que incluya solo lo necesario para que Python funcione
FROM python:3.13-slim

# 2. # 2. Traemos uv ya listo, sin tener que instalarlo con pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Crea una carpeta llamada /app si no existe dentro del contenedor
# Todo lo que se haga ahora se hace dentro de esta carpeta
WORKDIR /app

# 4. Copiamos solo la lista de dependencias con sus versiones 
# e instalamos las que necesita el proyecto.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# 5. Copia el resto del proyecto "COPY . ." y lo instalamos.
COPY . .
RUN uv sync --locked

# 6. Le decimos al contenedor dónde están los programas ya instalados (python, fastapi...)
ENV PATH="/app/.venv/bin:$PATH"

# 7. La app escucha en el puerto 8000
EXPOSE 8000

# 8. Comando que arranca la app cada vez que se enciende el contenedor
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

## Variables de entorno

Ya las tenemos creadas en nuestro archivo .env

## Construcción y prueba de la imagen del backend en solitario

> ‼️`Importante` -> Docker Desktop tiene que estar abierto.

### Paso 1: Construir la imagen

En la raiz del proyecto, ejecutamos el siguiente comando: `docker build -t crud-backend .`

- Lo que hace es construir la imagen dándole un nombre de etiqueta y decirle que los dockers y los archivos a copiar están en la carpeta donde estamos ahora.

### Paso 2: Arrancar un contenedor con esa imagen

Ejecutamos el siguiente comando: `docker run --name crud-backend-test -p 8000:8000 --env-file .env crud-backend`

> ‼️`Importante` -> Al arrancar el proyecto, hay que cambiar el url a localhost, porque si no aparecerá un error.

### Paso 3: Creación de redes

Creamos una red privada para meter contenedores y que puedan comunicarse entre si, a partir de ahí pueden encontrarse por su nombre.

1. Creamos la red: `docker network create crud-network`
2. Comprobamos que esa red existe con: `docker network ls`
3. Levantar **Postgres** conectado a esa red:
```
docker run --name crud-db `
  --network crud-network `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=<tu_contraseña_actual_del_env> `
  -e POSTGRES_DB=crud_user_db `
  -v crud_pgdata:/var/lib/postgresql/data `
  -p 5432:5432 `
  -d postgres:17
```
4. Comprobar que **Postgres** arrancó bien:
```
docker ps
docker logs crud-db
```
5. Arrancar el backend apuntando a Postgres:
```
docker run --name crud-backend-test `
   --network crud-network `                                                              
   -p 8000:8000 `                                                                        
   --env-file .env `
   -e DATABASE_URL="postgresql+psycopg://postgres:caialvaro7@crud-db:5432/crud_user_db" `
   crud-backend
```
6. Debería saltar un error al acceder a la siguiente URL: `http://localhost:8000/api/v1/users/`, en consola constará que la tabla users no existe. Lo arreglaremos en el siguiente paso.

## Ejecución de migraciones de Alembic dentro de Docker

Utilizaremos un contenedor de 'usar y tirar' solo para este tipo de comandos: se enciende, ejecuta la orden, y se apaga solo.

### Aplicar las migraciones existentes: `alembic upgrade head`

```
docker run --rm `
  --network crud-network `
  --env-file .env `
  -e DATABASE_URL="postgresql+psycopg://postgres:caialvaro7@crud-db:5432/crud_user_db" `
  crud-backend alembic upgrade head
```

¿Qué hace cada parte aquí?

1. ``--rm`` → en cuanto el contenedor termina se borra solo; solo lo necesitamos para ese instante y no queremos que siga ocupando espacio.
2. ``--network crud-network`` → lo mete en la misma red que `crud-db`, para que pueda encontrarlo por su nombre.
3. ``--env-file .env`` + ``-e DATABASE_URL=...`` → carga `APP_NAME`, `DEBUG` y `ALLOWED_ORIGINS` desde el archivo, y sobreescribe solo `DATABASE_URL` para que apunte a `crud-db` en vez de a `localhost`.
4. ``crud-backend alembic upgrade head`` → usa la misma imagen del backend, pero **sustituye** el `CMD` del Dockerfile (que arrancaría el servidor) por el comando de Alembic, solo para esta ejecución puntual.

### Generar una migración nueva: `alembic revision --autogenerate`

Hace falta cuando cambias tus modelos (`app/models/`) y necesitas que Alembic detecte la diferencia y escriba una migración nueva.

```
docker run --rm --network crud-network `
  --env-file .env `
  -e DATABASE_URL="postgresql+psycopg://postgres:caialvaro7@crud-db:5432/crud_user_db" `
  -v "${PWD}\alembic\versions:/app/alembic/versions" `
  crud-backend alembic revision --autogenerate -m "nombre_de_la_migracion"
```

> ‼️`Importante` -> Aquí hace falta añadir `-v "${PWD}\alembic\versions:/app/alembic/versions"` (un **bind mount**), y no es opcional. Sin esto, Alembic genera el archivo nuevo dentro de la copia del proyecto que vive en el contenedor, y al llevar `--rm`, en cuanto el comando termina esa copia (con el archivo nuevo dentro) se borra entera, sin haber tocado nunca tu carpeta real. El bind mount conecta tu carpeta `alembic\versions` real con la del contenedor, para que sea la misma carpeta vista desde los dos sitios, y el archivo nuevo aparezca de verdad en tu proyecto. Se monta solo esa carpeta (no todo `/app`) porque montar el proyecto entero pisaría el entorno virtual de Linux de la imagen con el de Windows de tu ordenador, y dejaría de funcionar.

### Problema: la migración inicial no creaba la tabla `users`

Al levantar `crud-db` desde cero y ejecutar `alembic upgrade head`, la migración terminaba "sin errores", pero al visitar `http://localhost:8000/api/v1/users/` seguía saliendo un error 500.

**Causa real:** el archivo `alembic/versions/b00bbed9d944_initial_migration.py` tenía el `upgrade()` vacío:

```python
def upgrade() -> None:
    pass
```

Esto pasó porque, en su momento, la tabla `users` ya existía en la base de datos local (creada antes con `Base.metadata.create_all(bind=engine)`, cuando esa línea todavía estaba activa en `main.py`). Al generar la migración con `alembic revision --autogenerate`, Alembic comparó el modelo `User` con la base de datos local y no encontró ninguna diferencia que anotar — de ahí el `pass`. Esa migración solo "funcionaba" en bases de datos que ya tenían la tabla creada por otra vía. En una base de datos nueva de verdad (como `crud-db`), no creaba nada.

**Solución — reescribir la migración para que sí cree la tabla:**

1. Generar el contenido correcto apuntando a una base de datos vacía (comando de la sección anterior, con el bind mount).
2. Copiar el `upgrade()` y `downgrade()` generados dentro de `b00bbed9d944_initial_migration.py`:

```python
def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('height', sa.Float(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
```

3. Borrar el archivo temporal generado en el paso 1 (ya está copiado dentro de la migración original).

> ‼️`Importante` -> No hace falta tocar la base de datos local: ya tiene la tabla `users` con las columnas correctas. El cambio solo afecta a bases de datos **nuevas** (Docker, un servidor real el día de mañana...), que ahora sí se construirán bien desde cero.

### Problema: las imágenes de Docker no se actualizan solas

Después de corregir la migración, `alembic upgrade head` seguía sin crear la tabla `users` en `crud-db`.

**Causa:** una imagen (`docker build`) es una **foto fija** del proyecto en el momento de construirla. Editar archivos después no la actualiza — el contenedor sigue usando la versión antigua congelada dentro de la imagen (la migración vacía).

**Solución:** reconstruir la imagen cada vez que se cambie código relevante:

```
docker build -t crud-backend .
```

> ‼️`Importante` -> A partir de ahora, cualquier cambio en el código (incluidas las migraciones) necesita `docker build` de nuevo antes de volver a usar el contenedor.

### Problema: PowerShell puede romper el JSON al pasar variables con `-e`

Al arrancar el backend con `-e ALLOWED_ORIGINS='["http://localhost:4200"]'` escrito a mano, la aplicación fallaba al arrancar con `SettingsError` / `JSONDecodeError`.

**Causa:** PowerShell no siempre entrega intactas las comillas dobles que van dentro de comillas simples al pasarlas a un programa externo como `docker`, así que el JSON llegaba mal formado.

**Solución:** dejar que esa variable (y las demás que no cambian) se lean directamente del `.env` con `--env-file`, y sobreescribir a mano solo lo que sí cambia (`DATABASE_URL`):

```
docker run --name crud-backend-test `
  --network crud-network `
  -p 8000:8000 `
  --env-file .env `
  -e DATABASE_URL="postgresql+psycopg://postgres:caialvaro7@crud-db:5432/crud_user_db" `
  crud-backend
```

### Pasos finales, en orden, para dejarlo todo funcionando desde cero

1. `docker build -t crud-backend .` → reconstruye la imagen con el código y la migración ya corregidos.
2. `docker stop crud-db; docker rm crud-db; docker volume rm crud_pgdata` → borra la base de datos de prueba por completo (su historial de migraciones estaba mal).
3. Recrear `crud-db` (comando de la sección "Creación de redes").
4. `docker run --rm --network crud-network --env-file .env -e DATABASE_URL="..." crud-backend alembic upgrade head` → aplica la migración ya corregida sobre la base de datos nueva.
5. `docker rm crud-backend-test` (si existe) y volver a arrancarlo con el comando de este apartado.
6. Probar `http://localhost:8000/api/v1/users/` → debería devolver `[]`.

## Creación del archivo .yaml

```
# Este archivo une los contenedores del proyecto (base de datos + backend) para
# poder levantarlos todos juntos con un solo comando: docker compose up
# Compose crea automáticamente una red privada y mete aquí dentro a todos los
# "services", para que puedan encontrarse entre sí por su nombre (db, backend),
# sin tener que crear la red a mano como hacíamos antes con "docker network create".

services:

  # ===============================
  # SERVICIO: BASE DE DATOS (Postgres)
  # ===============================
  db:
    # Imagen oficial de Postgres, versión 17
    image: postgres:17
    # Si el contenedor se cae por lo que sea, Docker intenta reiniciarlo solo
    restart: always
    # Variables que necesita la imagen oficial de Postgres para crear el
    # usuario, la contraseña y la base de datos la primera vez que arranca
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: caialvaro7
      POSTGRES_DB: crud_user_db
    # Guarda los datos fuera del contenedor, en el volumen "pgdata".
    # Así, aunque borremos el contenedor, los datos no se pierden
    volumes:
      - pgdata:/var/lib/postgresql/data
    # Conecta el puerto 5432 de mi ordenador con el 5432 del contenedor
    # (para poder conectarme desde fuera con herramientas como DBeaver)
    ports:
      - "5432:5432"

  # ===============================
  # SERVICIO: BACKEND (FastAPI)
  # ===============================
  backend:
    # En vez de usar una imagen ya hecha, la construye desde el Dockerfile
    # que hay en esta misma carpeta (el punto "." significa "aquí")
    build: .
    # Arranca "db" antes que "backend".
    # Ojo: solo controla el ORDEN de arranque, no espera a que Postgres
    # esté completamente listo para aceptar conexiones
    depends_on:
      - db
    # Carga APP_NAME, DEBUG y ALLOWED_ORIGINS directamente desde mi archivo .env
    env_file:
      - .env
    # Sobreescribe SOLO la variable DATABASE_URL del .env, porque dentro de
    # Docker la base de datos ya no se llama "localhost", se llama "db"
    # (el nombre del servicio de arriba, que Compose resuelve solo)
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:caialvaro7@db:5432/crud_user_db
    # Conecta el puerto 8000 de mi ordenador con el 8000 del contenedor
    ports:
      - "8000:8000"

# Declaramos el volumen con nombre para que Docker lo gestione y los datos
# de Postgres sobrevivan a un "docker compose down"
volumes:
  pgdata:
```