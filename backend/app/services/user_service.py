from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserNotFoundException
from app.models.user import User
from app.repositores.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

# Esta clase se encarga de validar todas las reglas de negocio que no puede hacer el 
class UserService:
    
    # Crea una instancia del Repository para acceder a la base de datos desde el Service.
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        
    # Crea un usuario nuevo
    # Si el usuario introducido tiene menos de 3 carácteres y el peso o la altura es menor que 0, saltará un error
    # El usuario tiene que ser mayor de edad
    def create_user(self, user: UserCreate) -> User:
        
        return self.repository.create_user(user)
    
    # Devuelve un usuario por su id
    # Si el usuario no existe saltará un error
    def get_user_by_id(self, user_id: int) -> User:
        
        user = self.repository.get_user_by_id(user_id)
        
        if user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        
        return user
    
    # Devuelve la lista de usuarios
    def get_users(self) -> list[User]:
        
        users = self.repository.get_users()
        
        return users
    
    # Devuelve un usuario actualizado
    # Si el usuario no existe saltará un error
    def update_user(self, user_id: int, user: UserUpdate) -> User:
        
        updated_user = self.repository.update_user(user_id, user)
        
        if updated_user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        
        return updated_user
    
    # Devuelve el usuario eliminado
    def delete_user_by_id(self, user_id: int) -> User:
        
        deleted_user = self.repository.delete_user_by_id(user_id)
        
        if deleted_user is None:
            raise UserNotFoundException(f"El usuario con el id: {user_id} no existe.")
        
        return deleted_user