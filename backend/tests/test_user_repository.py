from app.repositores.user_repository import UserRepository
from tests.helpers import make_fake_update_user, make_fake_user, make_fake_user_create


# ===============================
# CREATE TEST
# ===============================

def test_create_user_persists_to_database(db_session):

    # Creamos una instancia del repositorio utilizando la base de datos de pruebas
    repository = UserRepository(db_session)

    new_user = make_fake_user_create()

    # Guardamos el usuario en la base de datos
    result = repository.create_user(new_user)

    # Comrpobamos que se han guardado los siguientes cambios
    assert result.id is not None
    assert result.name == "Álvaro"
    assert result.age == 32
    assert result.height == 1.92
    assert result.weight == 94.1
    assert result.city == "Zaragoza"
    assert result.is_admin is False


# ===============================
# GET TEST
# ===============================

# Test para comprobar que si buscamos un id que no existe, el repositorio no lanza un error, solo devuelve null
def test_get_user_by_id_returns_none_if_not_exists(db_session):

    repository = UserRepository(db_session)

    # Buscamos un id que nunca se ha creado en esta base de datos de prueba
    result = repository.get_user_by_id(999)

    assert result is None


# Test para comprobar que si el usuario existe, el repositorio lo encuentra por su id
def test_get_user_by_id_returns_user_when_exists(db_session):
    repository = UserRepository(db_session)

    # Primero creamos un usuario real en la base de datos, para poder buscarlo después
    created = repository.create_user(
        make_fake_user_create()
    )

    # Lo buscamos por el id que nos devolvió la creación
    result = repository.get_user_by_id(created.id)

    # Comprobamos que el usuario encontrado es exactamente el que habíamos creado
    assert result is not None
    assert result.id == created.id
    assert result.name == created.name
    assert result.age == created.age
    assert result.height == created.height
    assert result.weight == created.weight
    assert result.city == created.city
    assert result.is_admin == created.is_admin


# Test para comprobar que si no hay usuarios guardados, la lista viene vacía
def test_get_users_returns_empty_list(db_session):

    repository = UserRepository(db_session)

    # Pedimos la lista de usuarios sin haber creado ninguno todavía
    users = repository.get_users()

    assert users == []
    assert len(users) == 0


# Test para comprobar que la lista devuelve todos los usuarios que hemos creado
def test_get_users_returns_all_users(db_session):

    repository = UserRepository(db_session)

    # Creamos dos usuarios distintos
    repository.create_user(make_fake_user_create())
    repository.create_user(make_fake_user_create(name="Jorge"))

    # Pedimos la lista completa
    users = repository.get_users()

    # Comprobamos que están los dos, en el mismo orden en el que se crearon
    assert len(users) == 2
    assert users[0].name == "Álvaro"
    assert users[1].name == "Jorge"


# ===============================
# UPDATE TEST
# ===============================

# Test para comprobar que al actualizar un usuario, los cambios quedan guardados de verdad
def test_update_user_persists_changes(db_session):

    repository = UserRepository(db_session)

    # Creamos el usuario original que luego vamos a modificar
    new_user = repository.create_user(make_fake_user_create())

    # Le mandamos los datos nuevos para sustituir los antiguos
    updated_user = repository.update_user(
        new_user.id,
        make_fake_update_user()
    )

    # Comprobamos que lo que devuelve update_user ya trae los datos nuevos
    assert updated_user.name == "Jorge"
    assert updated_user.age == 30
    assert updated_user.height == 1.88
    assert updated_user.weight == 88.2
    assert updated_user.city == "Barakaldo"
    assert updated_user.is_admin is True

    # Volvemos a leer el usuario desde cero, para comprobar que el cambio
    # no solo se devolvió, sino que quedó realmente guardado en la base de datos
    saved_user = repository.get_user_by_id(new_user.id)

    assert saved_user.name == "Jorge"
    assert saved_user.age == 30
    assert saved_user.height == 1.88
    assert saved_user.weight == 88.2
    assert saved_user.city == "Barakaldo"
    assert saved_user.is_admin is True


# Test para comprobar que si el usuario no existe, no se actualiza nada y devuelve null
def test_update_user_returns_none_if_not_exists(db_session):
    repository = UserRepository(db_session)

    # Intentamos actualizar un id que nunca se ha creado
    result = repository.update_user(999, make_fake_update_user())

    assert result is None


# ===============================
# DELETE TEST
# ===============================

# Test para comprobar que al borrar un usuario, este desaparece de verdad de la base de datos
def test_delete_user_by_id_removes_user(db_session):
    repository = UserRepository(db_session)

    # Creamos el usuario que luego vamos a borrar
    new_user = repository.create_user(make_fake_user_create())

    # Lo borramos por su id
    deleted_user = repository.delete_user_by_id(new_user.id)

    # Comprobamos que nos devuelve el mismo usuario que hemos borrado
    assert deleted_user.id == new_user.id
    assert deleted_user.name == new_user.name
    assert deleted_user.age == new_user.age

    # Y comprobamos que, si lo volvemos a buscar, ya no existe
    assert repository.get_user_by_id(deleted_user.id) is None
