from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.database_exceptions import DatabaseException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

# La clase Repository es una clase que se encarga de acceder a la base de datos
# Su responsabilidad es hacer los métodos CRUD
class UserRepository:
    
    # Este constructor devuelve la sesión creada por get_db
    def __init__(self, db: Session):
        self.db = db # Guarda esa sesión para poder utilizarla en cualquier método del repositorio
    
    # Método para crear un usuario
    # La función recibe el schema de UserCreate y devuelve un usuario.
    def create_user(self, user: UserCreate) -> User:
        
        # Convierte un objeto del schema de Pydantic (con los datos recibidos del JSON) en un modelo de SQLAlchemy.
        # model_dump() convierte el schema de Pydantic en un diccionario, ** lo desempaqueta en parámetros y User() crea el modelo de SQLAlchemy.
        # 1. model_dump -> {"name": "Álvaro", "edad": 32}
        # 2. ** -> {name="Álvaro", edad=32}
        # 3. User() -> User(name="Álvaro", age=32)
        # Se guarda en una variable llamada user_model
        user_model = User(**user.model_dump())
        
        try: 
            # Añade el objeto a la sesion de SQLAlchemy y le decimos que lo queremos guardar en la base de datos
            self.db.add(user_model)
            # Guarda los datos en la base de datos
            self.db.commit()
            # Vuelve a leer el usuario desde la base de datos para obtener su estado actualizado.
            self.db.refresh(user_model)
            
            # Devolvemos el usuario creado
            return user_model
        
        except Exception as e:
            # Revierte la transacción si ocurre un error al guardar los cambios.
            self.db.rollback()
            
            # y devuelve un error personalizado
            # si es otro error devuelve e -> Que sería la causa original
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e 
        
    # Método para recoger un usuario por su id, le pasamos el id y devolverá el usuario o none
    def get_user_by_id(self, user_id: int) -> User | None:
        
        # Variable que busca el usuario por su id
        user_model = self.db.get(User, user_id)
        
        # Si no se encuentra el usuario, se devuelve null
        if user_model is None:
            return None
        
        # Devuelve el usuario que encontramos por el id
        return user_model
    
    # Método que devuelve una lista de usuarios
    def get_users(self) -> list[User]:
        
        # scalars() extrae los objetos del modelo del resultado de la consulta.
        users = self.db.scalars(select(User)).all() # Si no hay usuarios, .all() devuelve []
        
        # Devuelve una lista de usuarios
        return users
    
    # Método para actualizar un usuario, el método recibirá la clase para actualizar y un id y devolverá un usuario o null
    def update_user(self, user_id: int, user: UserUpdate) -> User | None:
        
        # Variable que busca el usuario por su id
        user_model = self.db.get(User, user_id)
        
        # Si no se encuentra el usuario, se devuelve null
        if user_model is None:
            return None
        
        # Convierte los datos en un diccionario de Python
        user_data = user.model_dump()
        
        # .items() recorre el diccionario y devuelve la clave y el valor de cada elemento.
        # Ejemplo: key = "name" value = "Álvaro", key = "age" value = 32, etc...
        # setattr() coge el usuario encontrado por su id y actualiza sus atributos con los nuevos valores recibidos.
        for key, value in user_data.items():
            setattr(user_model, key, value)
        
        try:            
            # Guarda los datos en la base de datos
            self.db.commit()
            # refresh() vuelve a leer este objeto desde la base de datos y los actualiza
            self.db.refresh(user_model)
            
            # Devuelve el usuario actualizado
            return user_model
        
        except Exception as e:            
            # Revierte la transacción si ocurre un error al guardar los cambios.
            self.db.rollback()
            
            # y devuelve un error personalizado
            # si es otro error devuelve e -> Que sería la causa original
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e
        
    # Método para borrar un usuario, le pasamos el id y devolverá un booleano
    def delete_user_by_id(self, user_id: int) -> User | None:
        
        # Recogemos el usuario por su id
        user_model = self.db.get(User, user_id)
        
        # Si el usuario no existe devolverá None
        if user_model is None:
            return None
        
        try:            
            # Pasamos el usuario y lo borramos
            self.db.delete(user_model)
            # Hacemos commit
            self.db.commit()
            
        except Exception as e:            
            # Revierte la transacción si ocurre un error al guardar los cambios.
            self.db.rollback()
            
            # y devuelve un error personalizado
            # si es otro error devuelve e -> Que sería la causa original
            raise DatabaseException("Error al guardar los cambios en la base de datos.") from e
        
        # Devolvemos el usuario eliminado
        return user_model
        