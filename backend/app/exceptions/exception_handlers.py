from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import UserNotFoundException

##
# Damos formato a las excepciones
##
    
# Cuando un usuario no existe
async def user_not_found_exception_handler(
    request: Request, # Peticion HTTP que recibe la API
    exc: UserNotFoundException # Excepción que hemos creado
):  # Devuelve un JSON como respuesta con el estado de respuesta y el contenido que será de tipo string str(exc)
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc)
        }
    )

# Cuando hay un error al acceder a la base de datos  
async def database_exception_handler(
    request: Request, # Peticion HTTP que recibe la API
    exc: DatabaseException # Excepción que hemos creado
):  # Devuelve un JSON como respuesta con el estado de respuesta y el contenido que será de tipo string str(exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc)
        }
    )

# Función que registra todos los exception handler de la aplicación  
def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler) # Añade la excepción UserNotFoundException
    app.add_exception_handler(DatabaseException, database_exception_handler) # Añade la excepción DatabaseException