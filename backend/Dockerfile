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