import time
import logging

from fastapi import Request

# Sirve para crear un objeto logger (registrador de mensajes, como un print personalizado) asociado a este archivo concreto.
# logging.getLogger() -> función que obtiene o crea un logger
# __name__ -> Es una variable especial de Python que contiene el nombre del módulo actual
logger = logging.getLogger(__name__)

# El logging middleware sirve para dejar un rastro de lo que está ocurriendo para poder mantenerla y solucionar problemas.
async def logging_middleware(request: Request, call_next):
    
    # Guardamos el momento en el que llega la petición
    start_time = time.perf_counter()
    
    # Dejamos continuar la petición hacia el router,
    # esperamos a que termine toda la lógica de la API
    response = await call_next(request)
    
    # Cuando vuelve la respuesta, calculamos:
    # tiempo final - tiempo inicial = duración total de la petición
    process_time = time.perf_counter() - start_time
    
    # Creamos el mensaje del log
    logger.info(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.4f}s"
    )
    
    # Devuelve la respuesta
    return response