import time
from fastapi import Request

# Middleware encargado de medir cuánto tarda una petición HTTP
async def process_time_middleware(request: Request, call_next):

    # Guardamos el momento exacto en el que entra la petición al middleware
    start_time = time.perf_counter()
    
    # Dejamos continuar la petición hacia el router,
    # esperamos a que termine toda la lógica de la API
    response = await call_next(request)

    # Cuando vuelve la respuesta, calculamos:
    # tiempo final - tiempo inicial = duración total de la petición
    process_time = time.perf_counter() - start_time
    
    # Añadimos una cabecera personalizada a la respuesta HTTP
    # para que el cliente pueda saber cuánto tardó la API
    response.headers["X-Process-Time"] = str(process_time)

    # Devolvemos la respuesta modificada al cliente
    return response
    
    