# Es un middleware que añade cabeceras HTTP de seguridad a todas las respuestas de tu API
from fastapi import Request


async def security_headers_middleware(request: Request, call_next):

    # Dejamos que la petición continúe hacia el router
    response = await call_next(request)

    # Evita que la página pueda ser cargada dentro de un iframe
    response.headers["X-Frame-Options"] = "DENY"

    # Evita que el navegador intente interpretar otro tipo de contenido
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Obliga al navegador a utilizar HTTPS durante un tiempo determinado
    # Lo dejamos para producción
    # preload  -> Solicita incluir el dominio en la lista HSTS de los navegadores para activar HTTPS desde la primera visita.
    # includeSubDomains -> Solo poner si mi app va a tener subdominios
    # response.headers["Strict-Transport-Security"] = (
    #    "max-age=31536000"
    # )

    return response