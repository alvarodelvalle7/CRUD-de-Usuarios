# MagicMock crea un objeto que puede fingir ser cualquier cosa
# path sustituye una función real por un mock solo durante el test.
from unittest.mock import MagicMock, patch
import pytest

from app.services.user_service import UserService
from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import UserNotFoundException
from tests.helpers import make_fake_update_user, make_fake_user, make_fake_user_create

# ===============================
# CREATE TEST
# ===============================

# Test para comprobar que se crea a un usuario
@patch("app.services.user_service.UserRepository")
def test_create_user(mock_repo_class):

    # Obtenemos la instancia del repositorio falso
    mock_repo = mock_repo_class.return_value
    
    # Simulamos que se crea un usuario
    mock_repo.create_user.return_value = make_fake_user()
    
    # Creamos el servicio. Internamente utilizará el repositorio falso
    service = UserService(db=MagicMock())

    # Creamos los datos del nuevo usuario con sus credenciales
    new_user = make_fake_user_create()

    # Recogemos el usuario creado
    result = service.create_user(new_user)
    
    assert result.id == 1
    assert result.name == "Álvaro"
    assert result.age == 32
    assert result.height == 1.92
    assert result.weight == 94.1
    assert result.city == "Zaragoza"
    assert result.is_admin is False
    
    # Comprobamos que el repositorio fue llamado una única vez con el id 1    
    mock_repo.create_user.assert_called_once_with(new_user)


# Test para comprobar que un fallo al guardar en la base de datos no se
# oculta en el servicio, sino que se deja pasar tal cual hacia arriba
# (para que el exception handler de FastAPI la convierta en un 500)
@patch("app.services.user_service.UserRepository")
def test_create_user_propagates_database_exception(mock_repo_class):

    # Obtenemos la instancia del repositorio falso
    mock_repo = mock_repo_class.return_value

    # Simulamos que el repositorio falla al guardar en la base de datos
    mock_repo.create_user.side_effect = DatabaseException("Error al guardar los cambios en la base de datos.")

    # Creamos el servicio. Internamente utilizará el repositorio falso
    service = UserService(db=MagicMock())

    new_user = make_fake_user_create()

    # Comprobamos que el servicio no atrapa el error, lo deja subir sin modificarlo
    with pytest.raises(DatabaseException):
        service.create_user(new_user)
        
    mock_repo.create_user.assert_called_once_with(new_user)


# ===============================
# GET TEST
# ===============================

# Test para comprobar que se encuentra a un usuario por su id
# Sustituye la función real por esta de prueba hasta que dure el test
# Se le entrega a la función el objeto de prueba(mock_repo_class)
@patch("app.services.user_service.UserRepository")
def test_get_user_by_id_returns_user_when_found(mock_repo_class):
       
    # Obtenemos la instancia del repositorio falso
    mock_repo = mock_repo_class.return_value

    # Indicamos qué debe devolver el método get_user_by_id() cuando se llame
    mock_repo.get_user_by_id.return_value = make_fake_user()

    # Creamos el servicio. Internamente utilizará el repositorio falso
    service = UserService(db=MagicMock())

    # Ejecutamos el método que queremos probar
    result = service.get_user_by_id(1)

    expected = make_fake_user()
    
    # Comprobamos que el usuario devuelto tiene el nombre esperado
    assert result.id == expected.id
    assert result.name == expected.name
    assert result.age == expected.age
    assert result.height == expected.height
    assert result.weight == expected.weight
    assert result.city == expected.city
    assert result.is_admin == expected.is_admin
    
    # Comprobamos que el repositorio fue llamado una única vez con el id 1
    mock_repo.get_user_by_id.assert_called_once_with(1)


# Test cuando no encuentra un usuario por su id
@patch("app.services.user_service.UserRepository")
def test_get_user_by_id_when_user_not_found(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value

    # Simulamos que el repositorio no encuentra ningún usuario
    mock_repo.get_user_by_id.return_value = None

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Comprobamos que, si el usuario no existe, se lanza la excepción esperada
    with pytest.raises(UserNotFoundException):
        service.get_user_by_id(999)
        

# Test para comprobar que hay usuarios en la lista
@patch("app.services.user_service.UserRepository")
def test_get_users_returns_user_list(mock_repo_class):
    
    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que devuelve una lista con dos usuarios y uno tiene nombre
    mock_repo.get_users.return_value = [make_fake_user(id=1), make_fake_user(id=2, name="Marta")]

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real    
    service = UserService(db=MagicMock())

    # Recogemos la lista de usuarios
    result = service.get_users()

    # Debe devolver la cantidad de usuarios y el nombre Marta
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].name == "Marta"
    
    # Comprobamos que el servicio llamó una única vez al repositorio
    mock_repo.get_users.assert_called_once()
    
    
# Test para comprobar que la lista está vacía
@patch("app.services.user_service.UserRepository")
def test_get_users_when_list_is_empty(mock_repo_class):
    
    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que devuelve una lista vacía
    mock_repo.get_users.return_value = []

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real    
    service = UserService(db=MagicMock())

    # Recogemos la lista de usuarios
    result = service.get_users()

    # Debe devolver una lista vacia
    assert result == []
    
    # Comprobamos que el servicio llamó una única vez al repositorio
    mock_repo.get_users.assert_called_once()
    

# ===============================
# UPDATE TEST
# ===============================

# Test para comprobar que se actualiza un usuario correctamente cuando existe
@patch("app.services.user_service.UserRepository")
def test_update_user_returns_updated_user_when_found(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que el repositorio actualiza y devuelve el usuario con los nuevos datos
    mock_repo.update_user.return_value = make_fake_user(age=31, weight=94.0)

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Datos para actualizar el usuario existente
    update_data = make_fake_update_user()

    # Ejecutamos la actualización
    result = service.update_user(1, update_data)

    # Comprobamos que se han actualizado los campos esperados
    assert result.age == 31
    assert result.weight == 94.0

    # Comprobamos que el resto de datos siguen siendo correctos
    assert result.id == 1
    assert result.name == "Álvaro"
    assert result.city == "Zaragoza"
    assert result.is_admin is False
    
    # Comprobamos que el repositorio fue llamado con el id y los datos correctos, en ese orden
    mock_repo.update_user.assert_called_once_with(1, update_data)
    
    
# Test para comprobar que no se actualiza un usuario si no existe
@patch("app.services.user_service.UserRepository")
def test_update_user_raises_when_not_found(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que devuelve null si no encuentra el usuario
    mock_repo.update_user.return_value = None

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Datos para actualizar un usuario que no existe
    update_data = make_fake_update_user()

    # Comprobamos que si el id del usuario no existe, salta la excepción
    with pytest.raises(UserNotFoundException):
        service.update_user(999, update_data)
        
    mock_repo.update_user.assert_called_once_with(999, update_data)


# Test para comprobar que un fallo al guardar la actualización no se
# oculta en el servicio, sino que se deja pasar tal cual hacia arriba
@patch("app.services.user_service.UserRepository")
def test_update_user_propagates_database_exception(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que el repositorio falla al guardar los cambios
    mock_repo.update_user.side_effect = DatabaseException("Error al guardar los cambios en la base de datos.")

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    update_data = make_fake_update_user()

    # Comprobamos que el servicio no atrapa el error, lo deja subir sin modificarlo
    with pytest.raises(DatabaseException):
        service.update_user(1, update_data)
        
    # Comprobamos que el repositorio fue llamado con el id y los datos correctos, en ese orden
    mock_repo.update_user.assert_called_once_with(1, update_data)


# ===============================
# DELETE TEST
# ===============================

# Test para comprobar que se borra un usuario correctamente cuando existe
@patch("app.services.user_service.UserRepository")
def test_delete_user_returns_deleted_user_when_found(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que el repositorio encuentra y borra el usuario
    mock_repo.delete_user_by_id.return_value = make_fake_user(id=1)

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Ejecutamos el borrado
    result = service.delete_user_by_id(1)

    # Comprobamos que se devuelve el usuario borrado
    assert result.id == 1
    
    # Comprobamos que el repositorio fue llamado una única vez con el id correcto
    mock_repo.delete_user_by_id.assert_called_once_with(1)
    
    
# Test para comprobar que no se borra un usuario si no existe
@patch("app.services.user_service.UserRepository")
def test_delete_user_raises_when_not_found(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que devuelve null si no encuentra el usuario
    mock_repo.delete_user_by_id.return_value = None

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Comprobamos que si el id del usuario no existe, salta la excepción
    with pytest.raises(UserNotFoundException):
        service.delete_user_by_id(999)
    
    mock_repo.delete_user_by_id.assert_called_once_with(999)


# Test para comprobar que un fallo al borrar no se oculta en el servicio,
# sino que se deja pasar tal cual hacia arriba
@patch("app.services.user_service.UserRepository")
def test_delete_user_propagates_database_exception(mock_repo_class):

    # Obtenemos el repositorio falso que vamos a utilizar en este test
    mock_repo = mock_repo_class.return_value
    # Simulamos que el repositorio falla al borrar el usuario
    mock_repo.delete_user_by_id.side_effect = DatabaseException("Error al guardar los cambios en la base de datos.")

    # Creamos el servicio. Este utilizará el repositorio falso en lugar del real
    service = UserService(db=MagicMock())

    # Comprobamos que el servicio no atrapa el error, lo deja subir sin modificarlo
    with pytest.raises(DatabaseException):
        service.delete_user_by_id(1)
        
    # Comprobamos que el repositorio fue llamado una única vez con el id correcto
    mock_repo.delete_user_by_id.assert_called_once_with(1)
        
   
    
    