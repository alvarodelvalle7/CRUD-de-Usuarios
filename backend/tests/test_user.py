import pytest

from tests.helpers import make_fake_update_user, make_fake_user_payload

# ===============================
# TEST CREATE
# ===============================

# Test para comprobar que el endpoint create se realiza correctamente
# Le pasamos el función fixture de client que hace peticiones HTTP falsas a mi app
def test_create_user_returns_200_and_user_data(client):

    # Enviamos el usuario creado
    response = client.post(
        "/api/v1/users/",
        json=make_fake_user_payload()
    )

    # Comprueba que la respues es 200
    assert response.status_code == 200

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que se ha generado un id válido
    assert isinstance(body["id"], int)
    assert body["id"] > 0

    # Comprueba que los datos del usuario son los esperados
    assert body["name"] == "Álvaro"
    assert body["age"] == 32
    assert body["height"] == 1.92
    assert body["weight"] == 94.1
    assert body["city"] == "Zaragoza"
    assert body["is_admin"] is False

# Anotación para poner las restricciones de Pydantic
# Ejecuta el mismo test varias veces, cambiando cada vez el campo indicado
# por un valor inválido, para no repetir el mismo test tres veces casi igual
@pytest.mark.parametrize("field, invalid_value", [
    ("age", 17),        # menor de edad, viola ge=18
    ("height", -1.0),      # viola gt=0
    ("name", "Al"),       # menos de 3 caracteres
])
# Test para comprobar que el endpoint create no se realiza correctamente
def test_create_user_returns_422_when_data_is_invalid(client, field, invalid_value):

    # Cogemos un usuario válido de plantilla...
    payload = make_fake_user_payload()
    # ...y le rompemos a propósito el campo que toque en esta ejecución del test
    payload[field] = invalid_value

    response = client.post(
        "/api/v1/users/",
        json=payload
    )

    # Comprueba que la respuesta es 422
    assert response.status_code == 422

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que FastAPI explica por qué ha rechazado los datos
    assert "detail" in body


# ===============================
# TEST GET
# ===============================

# Test para comprobar que el endpoint get user devuelve el status 200
def test_get_user_by_id_returns_200_and_user_data(client):

    # Datos del usuario que vamos a crear primero, para luego poder pedirlo por su id
    payload = make_fake_user_payload()

    # Creamos el usuario en la base de datos de prueba
    create_response = client.post(
        "/api/v1/users/",
        json=payload
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    created_user = create_response.json()

    # Pedimos ese mismo usuario por el id que nos ha devuelto la creación
    response = client.get(
        f"/api/v1/users/{created_user['id']}"
    )

    # Comprueba que la respuesta es 200
    assert response.status_code == 200

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que el usuario devuelto es el mismo que hemos creado
    assert isinstance(body["id"], int)
    assert body["id"] == created_user["id"]
    assert body["name"] == payload["name"]
    assert body["age"] == payload["age"]
    assert body["height"] == payload["height"]
    assert body["weight"] == payload["weight"]
    assert body["city"] == payload["city"]
    assert body["is_admin"] == payload["is_admin"]


# Test para comprobar que el endpoint get users devuelve el status 200
def test_get_users_returns_200_and_user_list(client):

    # Datos del primer usuario
    payload = make_fake_user_payload()

    # Creamos el primer usuario
    client.post(
        "/api/v1/users/",
        json=payload
    )

    # Creamos un segundo usuario con otro nombre, para tener dos usuarios distintos guardados
    client.post(
        "/api/v1/users/",
        json=make_fake_user_payload(name="Jorge")
    )

    # Pedimos la lista completa de usuarios
    response = client.get(
        "/api/v1/users/"
    )

    # Comprueba que la respuesta es 200
    assert response.status_code == 200

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que ha devuelto exactamente los dos usuarios creados, en orden de creación
    assert len(body) == 2
    assert isinstance(body, list)

    assert body[0]["name"] == "Álvaro"
    assert body[1]["name"] == "Jorge"


# Test para comprobar que un id falso no se encuentra
def test_get_user_by_id_returns_404_when_not_found(client):

    # Pedimos un id que nunca hemos creado, así que no puede existir
    response = client.get("/api/v1/users/99999")

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que la respuesta es 404
    assert response.status_code == 404

    # Comprueba que el mensaje de error es el que lanza UserService
    assert body["detail"] == "El usuario con el id: 99999 no existe."


# Test para comprobar que una lista está vacía
def test_get_users_returns_empty_list_when_no_users_exist(client):

    # Pedimos la lista de usuarios sin haber creado ninguno antes
    response = client.get("/api/v1/users/")

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que la respuesta es 200
    assert response.status_code == 200

    # Comprueba que devuelve una lista vacia
    assert body == []
    assert isinstance(body, list)
    assert len(body) == 0


# ===============================
# TEST UPDATE
# ===============================

# Test para comprobar que un usuario se actualiza correctamente
def test_update_user_returns_200_when_user_updated(client):

    # Datos del usuario que vamos a crear primero, para luego poder actualizarlo
    payload = make_fake_user_payload()

    # Creamos el usuario original
    create_response = client.post(
        "/api/v1/users/",
        json=payload
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    created_user = create_response.json()

    # Enviamos los nuevos datos para sustituir al usuario creado
    response = client.put(
        f"/api/v1/users/{created_user['id']}",
        json=make_fake_update_user().model_dump()
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que devuelve un 200 status
    assert response.status_code == 200

    # El id no cambia, pero el resto de datos deben ser los nuevos que hemos enviado
    assert body["id"] == created_user["id"]
    assert body["name"] == "Jorge"
    assert body["age"] == 30
    assert body["height"] == 1.88
    assert body["weight"] == 88.2
    assert body["city"] == "Barakaldo"
    assert body["is_admin"] is True

# Test para comprobar que el usuario se actualiza correctamente y persiste en la base de datos
def test_update_user_returns_200_and_persists_changes(client):

    # Creamos el usuario
    create_response = client.post(
        "/api/v1/users/",
        json=make_fake_user_payload()
    )

    created_user = create_response.json()

    # Lo actualizamos
    update_response = client.put(
        f"/api/v1/users/{created_user['id']}",
        json=make_fake_update_user().model_dump()
    )

    # Lo volvemos a consultar mediante la API
    get_response = client.get(
        f"/api/v1/users/{created_user['id']}"
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = get_response.json()

    assert update_response.status_code == 200

    # Comprueba que los cambios se han guardado de verdad en la base de datos
    # (no solo que la respuesta del PUT los devolviera, sino que al volver a
    # consultar el usuario por GET, esos mismos cambios siguen ahí)
    assert body["name"] == "Jorge"
    assert body["age"] == 30
    assert body["height"] == 1.88
    assert body["weight"] == 88.2
    assert body["city"] == "Barakaldo"
    assert body["is_admin"] is True


# Test para comprobar que un usuario no se actualiza correctamente cuando no existe un usuario
def test_update_user_returns_404_when_user_does_not_exist(client):

    # Intentamos actualizar un id que nunca hemos creado
    response = client.put(
        "/api/v1/users/99999",
        json=make_fake_update_user().model_dump()
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que devuelve un 404 status
    assert response.status_code == 404

    # Devuelve un mensaje de error
    assert body["detail"] == "El usuario con el id: 99999 no existe."


# ===============================
# TEST DELETE
# ===============================

# Test para comprobar que se borra un usuario que sí existe
def test_delete_user_returns_200_when_user_exists(client):

    # Datos del usuario que vamos a crear primero, para luego poder borrarlo
    payload = make_fake_user_payload()

    # Creamos el usuario que vamos a borrar
    create_response = client.post(
        "/api/v1/users/",
        json=payload
    )

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    created_user = create_response.json()

    # Borramos ese usuario por su id
    response = client.delete(f"/api/v1/users/{created_user['id']}")

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    assert response.status_code == 200

    assert isinstance(body["id"], int)

    # Comprobamos que el usuario devuelto es el que se ha eliminado
    assert body["id"] == created_user["id"]
    assert body["name"] == created_user["name"]
    assert body["age"] == created_user["age"]
    assert body["height"] == created_user["height"]
    assert body["weight"] == created_user["weight"]
    assert body["city"] == created_user["city"]
    assert body["is_admin"] == created_user["is_admin"]


# Test para comprobar que el usuario se borra completamente de la base de datos
def test_delete_user_removes_user_from_database(client):

    # Creamos el usuario que vamos a borrar
    create_response = client.post(
        "/api/v1/users/",
        json=make_fake_user_payload()
    )

    created_user = create_response.json()

    # Lo borramos
    delete_response = client.delete(f"/api/v1/users/{created_user['id']}")

    # Intentamos volver a pedirlo por su id, para comprobar que ya no está
    response = client.get(f"/api/v1/users/{created_user['id']}")

    # El borrado tiene que haber funcionado (200)...
    assert delete_response.status_code == 200
    # ...y al buscarlo después, ya no debe existir (404)
    assert response.status_code == 404


# Test para comprobar que al borrar un usuario, ese usuario no existe
def test_delete_user_returns_404_when_user_does_not_exist(client):

    # Enviamos el id de un usuario ficticio para borrarlo
    response = client.delete("/api/v1/users/99999")

    # Convierte la respuesta JSON del endpoint en un diccionario de Python
    body = response.json()

    # Comprueba que devuelve un 404 status
    assert response.status_code == 404

    # Devuelve un mensaje de error
    assert body["detail"] == "El usuario con el id: 99999 no existe."
