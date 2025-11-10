import pytest
from unittest.mock import MagicMock
from db.repository.usuario import create_new_user, delete_usuario_by_id, update_usuario_by_id, lista_usuarios, retreive_usuario, update_state_usuario_by_id_logout
from db.models.usuario import Usuario
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioCreate


@pytest.fixture
def mock_db():
    """Mock de la sesión de la base de datos"""
    mock_session = MagicMock()
    return mock_session


def test_create_new_user(mock_db):
    """Prueba unitaria de create_new_user con mocks"""

    # Datos de prueba
    user_data = UsuarioCreate(nombre_usuario="testuser",  rol_usuario="Carnetizador")
    # Mock del usuario para evitar acceso a la BD real
    mock_user = Usuario(**user_data.dict())
    mock_db.add.return_value = None  # `add` no devuelve nada
    mock_db.commit.return_value = None  # `commit` no devuelve nada
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)  # Simula asignar un ID

    # Llamar a la función bajo prueba
    new_user = create_new_user(user_data, mock_db)

    # Verificaciones
    mock_db.add.assert_called_once()  # Verifica que `add
    # Verificar que los atributos sean iguales (comparación por valor, no referencia)
    added_user = mock_db.add.call_args[0][0]
    assert added_user.nombre_usuario == user_data.nombre_usuario
    assert added_user.rol_usuario == user_data.rol_usuario  #
    mock_db.commit.assert_called_once() # Verifica que commit
    mock_db.refresh.assert_called_once_with(added_user)  # `refresh` debe haberse llamado con el usuario

    # Verifica que los datos sean los correctos
    assert new_user.id == 1  # Simulación de ID asignado
    assert new_user.nombre_usuario == "testuser"
    assert new_user.rol_usuario == "Carnetizador"  # ⚠️ No r

def test_delete_usuario_by_id(mock_db):
    """Prueba unitaria de delete_usuario_by_id con mocks"""

    # ID del usuario a eliminar
    usuario_id = 1

    # Configurar el mock de la base de datos
    existing_usuario = MagicMock()
    mock_db.query.return_value.filter.return_value = existing_usuario
    existing_usuario.first.return_value = Usuario(id=usuario_id)  # Simular que el usuario existe

    # Llamar a la función bajo prueba
    result = delete_usuario_by_id(id, mock_db)

    # Verificaciones
    existing_usuario.delete.assert_called_once_with(synchronize_session=False)  # Verificar que delete fue llamado
    mock_db.commit.assert_called_once()  # Verificar que commit fue llamado
    assert result == 1  # Verificar que el resultado es 1 cuando se elimina correctamente

    # Ahora simular que el usuario no existe
    existing_usuario = []
    mock_db.query.return_value.filter.return_value = existing_usuario

    # Llamar a la función bajo prueba nuevamente
    result = delete_usuario_by_id(id, mock_db)

    # Verificacion
    assert result == 0

def test_update_usuario_by_id(mock_db):
    """Prueba unitaria de update_usuario_by_id con mocks"""

    # Datos de prueba
    user_data = UsuarioCreate(nombre_usuario="updateduser", rol_usuario="Administrador")
    exist_user = Usuario(id=1, nombre_usuario="updateduser", rol_usuario="Carnetizador")

    # Mock del usuario existente para evitar acceso a la BD real
    mock_db.query().filter().first.return_value = exist_user
    mock_db.commit.return_value = None  # `commit` no devuelve nada

    # Llamar a la función bajo prueba
    result = update_usuario_by_id(1, user_data, mock_db)

    # Verificaciones
    mock_db.query().filter().first.assert_called_once()  # Verifica que se ha llamado a `filter` una vez
    mock_db.commit.assert_called_once()  # Verifica que `commit` se ha llamado una vez
    mock_db.query().filter().update.assert_called_once_with(user_data.__dict__)  # Verifica que `update` se ha llamado con los datos correctos

    # Verifica que el resultado sea el esperado
    assert result == 1

def test_lista_usuarios (mock_db):
    """Prueba unitaria de lista_usuarios con mocks"""
    # Datos de prueba:
    usuarios_existentes = [
        Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador"),
        Usuario(id=2, nombre_usuario="usuario2", is_activo=False, rol_usuario="Administrador"),
        Usuario(id=3, nombre_usuario="usuario3", is_activo=True, rol_usuario="SuperAdmin")
    ]

    # Mock del query para retornar la lista de usuarios existentes
    mock_db.query().all.return_value = usuarios_existentes

    # Llamar a la función bajo prueba
    usuarios = lista_usuarios(mock_db)

    #Verificaciones
    mock_db.query().all.assert_called_once() # Verifica que se ha llamado a all al menos una vez

    # Verificar que los usuarios obtenidos son los mismos que los usuarios existentes
    assert usuarios == usuarios_existentes

    # Verificar que los atributos de los usuarios son correctos
    for i, usuario in enumerate(usuarios):
        assert usuario.id == usuarios_existentes[i].id
        assert usuario.nombre_usuario == usuarios_existentes[i].nombre_usuario
        assert usuario.is_activo == usuarios_existentes[i].is_activo
        assert usuario.rol_usuario == usuarios_existentes[i].rol_usuario

def test_retreive_usuario (mock_db):
    """Prueba unitaria de retreive_usuario con mocks"""
    # Datos de prueba:
    usuario_existente = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")
    id = 1

    # Mock del query para retornar la lista de usuarios existentes
    mock_db.query().filter().first.return_value = usuario_existente

    # Llamar a la función bajo prueba
    usuario = retreive_usuario(id, mock_db)

    #Verificaciones
    mock_db.query().filter().first.assert_called_once() # Verifica que se ha llamado a all al menos una vez

    # Verificar que el usuario obtenido es el existente
    assert usuario == usuario_existente

    # Verificar que los atributos del usuario obtenido son los del existente
    assert usuario.id == usuario_existente.id
    assert usuario.nombre_usuario == usuario_existente.nombre_usuario
    assert usuario.is_activo == usuario_existente.is_activo
    assert usuario.rol_usuario == usuario_existente.rol_usuario

def test_update_state_usuario_by_id_logout(mock_db):
    """Prueba unitaria de update_state_usuario_by_id_logout con mocks"""

    # Datos de prueba
    exist_user = Usuario(id=1, nombre_usuario="existinguser", is_activo=True, rol_usuario="Carnetizador")

    # Mock del usuario existente para evitar acceso a la BD real
    mock_db.query().filter().first.return_value = exist_user
    mock_db.commit.return_value = None  # `commit` no devuelve nada

    # Llamar a la función bajo prueba
    result = update_state_usuario_by_id_logout(1, mock_db)

    # Verificaciones
    mock_db.query().filter().first.assert_called_once()  # Verifica que se ha llamado a `filter` una vez
    mock_db.query().filter().update.assert_called_once_with(
        {"is_activo": False})  # Verifica que `update` se ha llamado con los datos correctos
    mock_db.commit.assert_called_once()  # Verifica que `commit` se ha llamado una vez

    # Verifica que el resultado sea el esperado
    assert result == 1
