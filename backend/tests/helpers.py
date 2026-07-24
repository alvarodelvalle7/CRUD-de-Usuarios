from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# ===============================
# FUNCIÓN MAKE FAKE USER
# ===============================

# Función de plantilla de usuario de prueba para no ir escribiendo a mano cada vez que se necesite uno nuevo.
# **overrides permite cambiar los atributos que se quieren en concreto.
def make_fake_user(**overrides):

    # Datos por defecto del usuario ficticio
    defaults = dict(
        id=1,
        name="Álvaro",
        age=32,
        height=1.92,
        weight=94.1,
        city="Zaragoza",
        is_admin=False
    )

    # Sustituye únicamente los campos que le pasemos al llamar a la función
    defaults.update(overrides)

    # Crea y devuelve un objeto User con los datos finales
    return User(**defaults)


# ===============================
# FUNCIÓN MAKE FAKE USER CREATE
# ===============================

# Devuelve un objeto UserCreate (schema de Pydantic)
def make_fake_user_create(**overrides):

    # Datos por defecto del usuario ficticio    
    defaults = dict(
        name="Álvaro",
        age=32,
        height=1.92,
        weight=94.1,
        city="Zaragoza",
        is_admin=False
    )
    
    # Sustituye únicamente los campos que le pasemos al llamar a la función
    defaults.update(overrides)

    # Crea y devuelve un objeto UserCreate con los datos finales
    return UserCreate(**defaults)


# ===============================
# FUNCIÓN MAKE FAKE USER UPDATE
# ===============================

# Devuelve un objeto UserCreate (schema de Pydantic)
def make_fake_update_user(**overrides):

    # Datos por defecto del usuario ficticio    
    defaults = dict(
        name="Jorge",
        age=30,
        height=1.88,
        weight=88.2,
        city="Barakaldo",
        is_admin=True
    )
    
    # Sustituye únicamente los campos que le pasemos al llamar a la función
    defaults.update(overrides)

    # Crea y devuelve un objeto UserCreate con los datos finales
    return UserUpdate(**defaults)


# ===============================
# FUNCIÓN MAKE FAKE USER PAYLOAD
# ===============================

# Devuelve un objeto UserCreate (schema de Pydantic)
def make_fake_user_payload(**overrides):

    # Datos por defecto del usuario ficticio    
    defaults = {
        "id": 1,
        "name": "Álvaro",
        "age": 32,
        "height": 1.92,
        "weight": 94.1,
        "city": "Zaragoza",
        "is_admin": False
    }
    
    # Sustituye únicamente los campos que le pasemos al llamar a la función
    defaults.update(overrides)

    # Devuelve el usuario en formato JSON
    return defaults