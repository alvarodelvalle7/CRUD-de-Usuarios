# ============================
# FASE 1: COMPILAR LA APP
# ============================

# 1. Imagen con Node.js 22 ya instalado (versión "alpine": mínima, para que pese poco)
FROM node:22-alpine AS build

# 2. Activa pnpm dentro de la imagen, sin tener que instalarlo aparte.
# Node ya trae "corepack" de fábrica; solo hay que encenderlo.
RUN corepack enable

# 3. Igual que en el Dockerfile del backend: crea /app dentro del contenedor
# y todo lo que sigue se hace ahí.
WORKDIR /app

# 4. Copiamos solo lo necesario para instalar dependencias primero
# (así, si el código cambia pero las dependencias no, Docker reutiliza este paso y va más rápido)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# 5. Copiamos el resto del proyecto y lo compilamos para producción
COPY . .
RUN pnpm exec ng build

# ============================
# FASE 2: SERVIR LA APP YA COMPILADA
# ============================

# 6. Empezamos de cero con una imagen distinta: Nginx, un servidor web ligero
FROM nginx:alpine

# 7. Copiamos SOLO los ficheros ya compilados desde la fase "build" de arriba
# (fíjate en "--from=build" — así no arrastramos Node, pnpm ni node_modules a la imagen final)
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

# 8. Copiamos nuestra propia configuración de Nginx (la crearemos en el paso 2)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 9. Nginx escucha por defecto en el puerto 80
EXPOSE 80

# 10. Comando que arranca Nginx cada vez que se enciende el contenedor
CMD ["nginx", "-g", "daemon off;"]
