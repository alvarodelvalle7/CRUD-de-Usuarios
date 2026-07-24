from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    
    name: str = Field( ..., min_length=3, max_length=100, description="Nombre del Usuario", examples=["Álvaro"])
    age: int = Field( ..., ge=18, description="Edad del Usuario", examples=[30])
    height: float = Field( ..., gt=0, description="Altura del Usuario", examples=[1.92])
    weight: float = Field( ..., gt=0, description="Peso del Usuario", examples=[95.1])
    city: Optional[str] = Field( default=None, description="Ciudad de Nacimiento del Usuario", examples=["Zaragoza"])
    is_admin: bool = Field(..., description="Tipo de Usuario", examples=[False])
    
    # Permite que Pydantic lea los atributos de un objeto (ej. un modelo de SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    