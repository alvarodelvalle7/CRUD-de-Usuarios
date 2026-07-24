# Apuntes de Docker (para Python/FastAPI, PostgreSQL y Angular)

> Objetivo de este documento: entender Docker con el mínimo tecnicismo posible y ver ejemplos reales aplicables a un backend en Python (FastAPI + `uv`), una base de datos PostgreSQL y un frontend en Angular.

---

## 1. ¿Qué es Docker, en cristiano?

Imagina que tienes una app que funciona perfecto en tu ordenador, pero al subirla a un servidor (o al ordenador de un compañero) deja de funcionar porque falta una versión de Python, o Postgres está configurado distinto. A esto se le llama el problema de **"en mi máquina funciona"**.

**Docker resuelve esto metiendo tu aplicación, junto con todo lo que necesita para funcionar (Python, librerías, configuración...), dentro de una "caja" cerrada y portable.** Esa caja se comporta exactamente igual en tu ordenador, en el del compañero o en un servidor en la nube.

> Definición oficial: *"Docker es una plataforma abierta para desarrollar, distribuir y ejecutar aplicaciones"*, que separa la aplicación de la infraestructura donde corre. — [Docker Docs – Overview](https://docs.docker.com/get-started/docker-overview/)

**Analogía:** piensa en un contenedor de mercancías de un barco. Da igual lo que lleve dentro (ropa, comida, muebles): la grúa del puerto, el camión y el barco lo mueven igual porque el contenedor tiene una forma estándar. Docker hace lo mismo con el software.

---

## 2. Vocabulario clave (con analogías)

| Concepto | Qué es | Analogía |
|---|---|---|
| **Imagen** (*Image*) | Plantilla de solo lectura con todo lo necesario para ejecutar tu app (código, Python, dependencias...) | El plano de una casa |
| **Contenedor** (*Container*) | Una instancia en ejecución de una imagen | La casa ya construida a partir del plano |
| **Dockerfile** | Archivo de texto con las instrucciones para construir una imagen | La receta de cocina |
| **Docker Compose** | Herramienta para levantar varios contenedores a la vez (backend + BD + frontend) y que se hablen entre ellos | El director de orquesta |
| **Volumen** (*Volume*) | Carpeta persistente fuera del contenedor, para que los datos no se pierdan al borrarlo | Un disco duro externo |
| **Registro** (*Registry*) | Lugar donde se guardan y descargan imágenes ya hechas (ej. Docker Hub) | Una tienda de apps |

> Fuente: *"Una imagen es una plantilla de solo lectura con instrucciones para crear un contenedor"*; *"un contenedor es un entorno ligero y aislado donde corre tu aplicación"* — [Docker Docs – Overview](https://docs.docker.com/get-started/docker-overview/)

**Punto importante:** una imagen **no cambia** una vez construida (es de solo lectura). Si necesitas actualizar algo, construyes una imagen nueva. Los contenedores sí son "desechables": puedes borrarlos y volver a crearlos desde la imagen sin miedo, **siempre que los datos importantes vivan en un volumen** (más sobre esto en la sección de Postgres).

---

## 3. El Dockerfile: la receta paso a paso

Un Dockerfile es una lista de instrucciones, cada una crea una "capa" (*layer*) de la imagen. Las instrucciones más comunes:

```dockerfile
FROM python:3.13-slim   # De qué imagen "base" partimos
WORKDIR /app             # Carpeta de trabajo dentro del contenedor
COPY . .                 # Copia archivos de tu ordenador al contenedor
RUN pip install ...      # Ejecuta un comando AL CONSTRUIR la imagen
ENV VARIABLE=valor        # Define una variable de entorno
EXPOSE 8000               # Documenta qué puerto usa la app (informativo)
CMD ["comando", "arg"]    # Comando que se ejecuta AL ARRANCAR el contenedor
```

**¿Por qué importa el orden de las instrucciones?** Docker cachea cada capa. Si copias primero los archivos que cambian poco (dependencias) y luego los que cambian mucho (tu código), Docker reutiliza la caché de las capas de dependencias y solo reconstruye lo que realmente cambió. Esto hace que reconstruir la imagen sea mucho más rápido tras cada cambio de código.

> Fuente oficial: *"Siempre que sea posible, usa imágenes base actuales y oficiales"* y ordena las instrucciones para aprovechar la caché de capas — [Docker Docs – Best practices](https://docs.docker.com/build/building/best-practices/)

**`RUN` vs `CMD`:** `RUN` se ejecuta una vez, mientras se **construye** la imagen (ej. instalar dependencias). `CMD` se ejecuta cada vez que **arranca** un contenedor a partir de esa imagen (ej. arrancar el servidor). Es un error común confundirlos.

---

## 4. Docker aplicado a tu backend (Python + FastAPI + `uv`)

### 4.1 La imagen oficial de Python

Docker Hub ofrece varias "variantes" de la imagen oficial de Python:

- **`python:3.13`** → completa, con paquetes de Debian ya incluidos. Más pesada.
- **`python:3.13-slim`** → solo lo mínimo necesario para ejecutar Python. **Recomendada para producción**: mismo comportamiento, imagen mucho más ligera.
- **`python:3.13-alpine`** → aún más pequeña, pero usa una librería C distinta (`musl` en vez de `glibc`), lo que a veces da problemas con paquetes que compilan código nativo (como `psycopg`). Para empezar, mejor evitarla.

> Fuente: *"La variante `slim` no contiene los paquetes de Debian comunes... solo los mínimos necesarios para ejecutar Python"* — [Docker Hub – python](https://hub.docker.com/_/python)

### 4.2 Dockerfile para un proyecto con `uv` (como el tuyo)

Como tu proyecto usa `uv` (con `pyproject.toml` y `uv.lock`) en vez de `pip` + `requirements.txt`, el propio equipo de `uv` (Astral) publica el patrón oficial recomendado:

```dockerfile
# Imagen base oficial de Python
FROM python:3.13-slim

# Copiamos el binario de uv desde su imagen oficial (no hace falta instalarlo con pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 1. Copiamos SOLO los archivos de dependencias primero.
#    Así, si solo cambia tu código (no las dependencias), Docker reutiliza esta capa
#    y no vuelve a descargar/instalar todo, ahorrando muchísimo tiempo.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

# 2. Ahora copiamos el resto del código de la aplicación
COPY . .
RUN uv sync --locked

# 3. Añadimos el entorno virtual creado por uv al PATH,
#    para poder ejecutar comandos directamente sin "uv run"
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Comando oficial recomendado por FastAPI para producción
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

**Desglose de las partes menos obvias:**

- **`COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/`**: en vez de instalar `uv` con `pip install uv` (que sería más lento), copiamos directamente el ejecutable ya compilado desde la imagen oficial de `uv`. Es el patrón que recomienda la propia documentación de Astral.
- **`uv sync --locked`**: instala exactamente las versiones fijadas en `uv.lock` (no versiones "más nuevas que puedan romper cosas"). `--no-install-project` en el primer `sync` evita instalar tu propio código todavía — solo las dependencias — para que esa capa se cachee de forma independiente.
- **`fastapi run app/main.py`**: es el comando oficial que recomienda FastAPI para producción (usa Uvicorn por debajo, pero con configuración de producción). Es distinto de `fastapi dev`, que solo debes usar en desarrollo (recarga automática, más "chatty").

> Fuentes: [uv – Docker integration guide](https://docs.astral.sh/uv/guides/integration/docker/) · [FastAPI – Deploy with Docker](https://fastapi.tiangolo.com/deployment/docker/)

### 4.3 El archivo `.dockerignore`

Igual que `.gitignore` evita subir archivos a Git, `.dockerignore` evita copiar archivos innecesarios (o sensibles) a la imagen:

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
.git/
```

**Por qué es importante excluir `.venv/`:** el entorno virtual de tu ordenador está compilado para *tu* sistema operativo (Windows). Dentro del contenedor (Linux) no serviría y solo ocuparía espacio de más — `uv` crea su propio entorno virtual nuevo dentro del contenedor.

**Por qué excluir `.env`:** nunca debes "hornear" (incluir) secretos como contraseñas de base de datos dentro de la imagen — cualquiera con acceso a la imagen podría leerlos. Las variables de entorno reales se pasan al arrancar el contenedor (`docker run -e ...` o la sección `environment:` de Docker Compose), no copiándolas dentro.

---

## 5. Docker aplicado a PostgreSQL

Para desarrollo, normalmente **no construyes tu propia imagen de Postgres** — usas la oficial directamente:

```bash
docker run --name todoapp-db \
  -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=supersecreta \
  -e POSTGRES_DB=todoapp \
  -p 5432:5432 \
  -v todoapp_pgdata:/var/lib/postgresql/data \
  -d postgres:17
```

**Desglose:**

- **`POSTGRES_PASSWORD`** es la única variable **obligatoria**. Sin ella, el contenedor no arranca.
- **`POSTGRES_USER`** y **`POSTGRES_DB`**: opcionales. Si no las pones, usa `postgres` por defecto para ambas.
- **`-p 5432:5432`**: mapea el puerto 5432 de tu ordenador al puerto 5432 del contenedor (para poder conectarte desde fuera, ej. desde tu FastAPI local o un cliente de BD).
- **`-v todoapp_pgdata:/var/lib/postgresql/data`**: esto es **crítico**. Es un volumen que guarda los datos fuera del contenedor. Si borras el contenedor sin este volumen, **pierdes toda la base de datos**. Con el volumen, puedes borrar y recrear el contenedor cuantas veces quieras sin perder nada.

> Fuente: *"`POSTGRES_PASSWORD` es obligatoria... no puede estar vacía"*; el volumen debe montarse en `/var/lib/postgresql/data` (para PostgreSQL 17 y anteriores) o los datos **no persistirán** — [Docker Hub – postgres](https://hub.docker.com/_/postgres)

---

## 6. Docker aplicado a Angular (frontend)

Angular es distinto a tu backend: cuando "compilas" un proyecto Angular (`ng build`), el resultado son solo **archivos estáticos** (HTML, CSS, JS). No necesita Node.js para funcionar en producción — Node solo hace falta para *construir* esos archivos.

Por eso, la imagen para Angular se hace con una técnica llamada **multi-stage build** (construcción en varias fases): una fase "obrero" que compila con Node, y una fase final, mucho más ligera, que solo sirve los archivos ya construidos con un servidor web (Nginx).

```dockerfile
# --- FASE 1: Construcción ---
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- FASE 2: Servido en producción ---
FROM nginxinc/nginx-unprivileged:alpine
COPY --chown=nginx:nginx --from=builder /app/dist/*/browser /usr/share/nginx/html
EXPOSE 8080
```

**Desglose:**

- **Fase 1 (`builder`)**: usa una imagen de Node (pesada, con todo lo necesario para compilar) solo para generar los archivos finales con `npm run build`.
- **`COPY --from=builder ...`**: la fase 2 **no hereda nada** de la fase 1, excepto lo que copiemos explícitamente. Así, la imagen final no contiene Node.js, `node_modules` ni el código fuente — solo los archivos estáticos ya compilados. Esto reduce muchísimo el tamaño final (de cientos de MB a unos pocos MB) y la superficie de ataque (menos cosas instaladas = menos vulnerabilidades posibles).
- **`nginxinc/nginx-unprivileged`**: variante de Nginx que corre como usuario normal (no root) por seguridad — buena práctica recomendada también por Docker.
- **`/usr/share/nginx/html`**: es la carpeta donde Nginx sirve archivos estáticos por defecto.

> Este patrón es el mismo que documenta oficialmente Docker para Angular — [Docker Docs – Containerize an Angular app](https://docs.docker.com/guides/angular/containerize/) · imagen base de Nginx — [Docker Hub – nginx](https://hub.docker.com/_/nginx)

No necesitas implementar esto todavía (aún no tienes frontend), pero así sabrás cómo encajará cuando llegue el momento.

---

## 7. Docker Compose: uniendo todas las piezas

Cuando tienes varios contenedores que deben funcionar juntos (backend + base de datos + frontend), en vez de arrancarlos uno a uno a mano con `docker run`, se define todo en **un solo archivo** (`compose.yaml`) y se levanta todo con un solo comando.

> Definición oficial: *"Docker Compose es una herramienta para definir y ejecutar aplicaciones multi-contenedor"* — [Docker Docs – Compose overview](https://docs.docker.com/compose/)

Ejemplo adaptado a la estructura de **ToDoApp** (backend + base de datos; el frontend se añadiría igual el día que exista):

```yaml
services:
  db:
    image: postgres:17
    restart: always
    environment:
      POSTGRES_USER: todoapp
      POSTGRES_PASSWORD: supersecreta
      POSTGRES_DB: todoapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .              # Construye la imagen usando el Dockerfile de esta carpeta
    depends_on:
      - db                # Arranca "db" antes que "backend"
    environment:
      DATABASE_URL: postgresql+psycopg://todoapp:supersecreta@db:5432/todoapp
    ports:
      - "8000:8000"

volumes:
  pgdata:
```

**Desglose de lo no evidente:**

- **`depends_on: - db`**: le dice a Compose que arranque `db` antes que `backend`. **Ojo:** esto solo controla el *orden de arranque*, no espera a que Postgres esté realmente listo para aceptar conexiones (eso se resuelve con reintentos de conexión en tu app o con un `healthcheck`, algo que podemos ver más adelante si hace falta).
- **`db:5432` dentro de `DATABASE_URL`**: dentro de la red interna que crea Docker Compose automáticamente, cada servicio puede llamar a otro **por su nombre** (`db`) como si fuera un nombre de dominio. No hace falta usar `localhost` ni IPs — Compose resuelve `db` automáticamente al contenedor de Postgres.
- **`volumes: pgdata:`** (al final, fuera de los servicios): declara el volumen con nombre para que Docker lo gestione y persista entre reinicios, tal como vimos en la sección de Postgres.

**Comandos básicos:**

```bash
docker compose up -d      # Levanta todos los servicios en segundo plano
docker compose down       # Los para y elimina (el volumen "pgdata" NO se borra)
docker compose logs -f backend   # Ver logs en tiempo real de un servicio concreto
```

---

## 8. Buenas prácticas — resumen rápido

| Práctica | Por qué |
|---|---|
| Usa imágenes oficiales y variantes `slim`/`alpine` cuando puedas | Menos tamaño, menos superficie de vulnerabilidades |
| Copia primero lo que cambia poco (dependencias), el código al final | Aprovecha la caché de capas → builds más rápidos |
| Usa `.dockerignore` | Evita copiar secretos (`.env`) o basura (`.venv`, `__pycache__`) a la imagen |
| Usa *multi-stage builds* cuando compiles algo (Angular, o binarios) | Imagen final más pequeña y sin herramientas de compilación innecesarias |
| No metas contraseñas dentro del Dockerfile ni de la imagen | Se pasan como variables de entorno al arrancar el contenedor, no se "hornean" dentro |
| Usa volúmenes para todo lo que deba sobrevivir a un `docker compose down` | Los contenedores son desechables; los datos, no |
| Ejecuta procesos como usuario no root cuando sea posible (`USER`) | Reduce el impacto si alguien compromete el contenedor |

> Fuente: [Docker Docs – Building best practices](https://docs.docker.com/build/building/best-practices/)

---

## 9. Chuleta de comandos esenciales

```bash
docker build -t nombre-imagen .        # Construye una imagen a partir del Dockerfile
docker run -p 8000:8000 nombre-imagen  # Ejecuta un contenedor a partir de una imagen
docker ps                              # Lista contenedores en ejecución
docker ps -a                           # Lista TODOS los contenedores (incluidos parados)
docker logs -f nombre-contenedor       # Ver logs en tiempo real
docker exec -it nombre-contenedor bash # Abrir una terminal DENTRO de un contenedor en marcha
docker compose up -d                   # Levantar todo el stack definido en compose.yaml
docker compose down                    # Parar y eliminar los contenedores del stack
```

---

## Fuentes verificadas

- [Docker Docs – Docker overview (imagen, contenedor, definiciones)](https://docs.docker.com/get-started/docker-overview/)
- [Docker Docs – Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker Hub – Imagen oficial de Python](https://hub.docker.com/_/python)
- [Docker Hub – Imagen oficial de PostgreSQL](https://hub.docker.com/_/postgres)
- [Docker Hub – Imagen oficial de Nginx](https://hub.docker.com/_/nginx)
- [Docker Docs – Compose overview](https://docs.docker.com/compose/)
- [Docker Docs – Containerize an Angular application (guía oficial)](https://docs.docker.com/guides/angular/containerize/)
- [uv (Astral) – Docker integration guide](https://docs.astral.sh/uv/guides/integration/docker/)
- [FastAPI – Deploy with Docker](https://fastapi.tiangolo.com/deployment/docker/)
