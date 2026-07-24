from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users", # Todas las rutas comenzarán por user
    tags=["Users"] # Al entrar en Swagger se etiquetan todos los endpoints dependiendo de la etiqueta de cada uno
)

# ENDPOINT POST PARA CREAR USUARIO
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    
    service = UserService(db)
    
    return service.create_user(user)

# ENDPOINT GET PARA LEER UNA LISTA DE USUARIOS
@router.get("/", response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]) -> list[UserResponse]:
    
    service = UserService(db)
    
    return service.get_users()

# ENDPOINT GET PARA LEER UN USUARIO
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    
    service = UserService(db)
    
    return service.get_user_by_id(user_id)

# ENDPOINT PUT PARA ACTUALIZAR UN USUARIO
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    
    service = UserService(db)
    
    return service.update_user(user_id, user)

# ENDPOINT DELETE PARA BORRAR UN USUARIO
@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    
    service = UserService(db)
    
    return service.delete_user_by_id(user_id)
    

