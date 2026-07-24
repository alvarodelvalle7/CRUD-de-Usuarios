import uuid

from fastapi import Request


async def request_id_middleware(request: Request, call_next):

    # Creamos un identificador único para esta petición
    request_id = str(uuid.uuid4())

    # Guardamos el ID dentro del objeto request
    request.state.request_id = request_id

    # Continuamos hacia el router
    response = await call_next(request)

    # Añadimos el ID en la respuesta HTTP
    response.headers["X-Request-ID"] = request_id

    return response