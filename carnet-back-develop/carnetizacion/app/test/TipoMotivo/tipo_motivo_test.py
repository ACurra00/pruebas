from db.models.tipo_motivo import TipoMotivo
from schemas.tipo_motivo import TipoMotivoCreate
from sqlalchemy.orm import Session
from db.repository.tipo_motivos import create_tipo_motivo, retreive_motivo, list_motivos, update_motivo_by_id
from db.repository.tipo_motivos import delete_tipo_motivo_by_id
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_db():
    """Mock de la sesión de la base de datos"""
    mock_session = MagicMock()
    return mock_session

def test_create_tipo_motivo(mock_db):
    """Prueba unitaria de create_tipo_motivo con mocks"""

    # Datos de prueba
    #estado = "Solicitado"
    motivo_data = TipoMotivoCreate(nombre_motivo = "Cambio de rol")
    # Mock del usuario para evitar acceso a la BD real
    mock_motivo = TipoMotivo(**motivo_data.dict())
    mock_db.add.return_value = None  # `add` no devuelve nada
    mock_db.commit.return_value = None  # `commit` no devuelve nada
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)  # Simula asignar un ID

    # Llamar a la función bajo prueba
    new_motivo = create_tipo_motivo(motivo_data, mock_db)

    # Verificaciones
    mock_db.add.assert_called_once()  # Verifica que `add
    # Verificar que los atributos sean iguales (comparación por valor, no referencia)
    added_motivo= mock_db.add.call_args[0][0]
    assert added_motivo.nombre_motivo == motivo_data.nombre_motivo
    mock_db.commit.assert_called_once() # Verifica que commit
    mock_db.refresh.assert_called_once_with(added_motivo)  # `refresh` debe haberse llamado con el usuario

    # Verifica que los datos sean los correctos
    assert new_motivo.id == 1  # Simulación de ID asignado
    assert new_motivo.nombre_motivo == "Cambio de rol"

def test_delete_tipo_motivo_by_id(mock_db):
    """Prueba unitaria de delete_tipo_motivo_by_id con mocks"""

    # ID del motivo a eliminar
    motivo_id = 1

    # Configurar el mock de la base de datos
    existing_motivo = MagicMock()
    mock_db.query.return_value.filter.return_value = existing_motivo
    existing_motivo.first.return_value = TipoMotivo(id_motivo=motivo_id)  # Simular que el motivo existe

    # Llamar a la función bajo prueba
    result = delete_tipo_motivo_by_id(motivo_id, mock_db)

    # Verificaciones
    existing_motivo.delete.assert_called_once_with(synchronize_session=False)  # Verificar que delete fue llamado
    mock_db.commit.assert_called_once()  # Verificar que commit fue llamado
    assert result == 1  # Verificar que el resultado es 1 cuando se elimina correctamente

    # Ahora simular que el motivo no existe
    existing_motivo = []
    mock_db.query.return_value.filter.return_value = existing_motivo

    # Llamar a la función bajo prueba nuevamente
    result = delete_tipo_motivo_by_id(motivo_id, mock_db)

    # Verificacion
    assert result == 0

def test_update_motivo_by_id(mock_db):
    """Prueba unitaria de update_motivo_by_id con mocks"""

    # Datos de prueba
    motivo_data = TipoMotivoCreate(nombre_motivo = "Cambio de rol")
    exist_motivo = TipoMotivo(id_motivo=1, nombre_motivo="Cambio de area")

    # Mock del motivo existente para evitar acceso a la BD real
    mock_db.query().filter().first.return_value = exist_motivo
    mock_db.commit.return_value = None  # `commit` no devuelve nada

    # Llamar a la función bajo prueba
    result = update_motivo_by_id(1, motivo_data, mock_db)

    # Verificaciones
    mock_db.query().filter().first.assert_called_once()  # Verifica que se ha llamado a `filter` una vez
    mock_db.commit.assert_called_once()  # Verifica que `commit` se ha llamado una vez
    mock_db.query().filter().update.assert_called_once_with(motivo_data.__dict__)  # Verifica que `update` se ha llamado con los datos correctos

    # Verifica que el resultado sea el esperado
    assert result == 1

def test_list_motivos (mock_db):
    """Prueba unitaria de list_motivos con mocks"""

    # Datos de prueba:
    motivos_existentes = [
        TipoMotivo(id_motivo=1, nombre_motivo="Cambio de rol"),
        TipoMotivo(id_motivo=2, nombre_motivo="Cambio de nombre"),
        TipoMotivo(id_motivo=3, nombre_motivo="Cambio de area")
    ]

    # Mock del query para retornar la lista de motivos existentes
    mock_db.query().all.return_value = motivos_existentes

    # Llamar a la función bajo prueba
    motivos = list_motivos(mock_db)

    #Verificaciones
    mock_db.query().all.assert_called_once() # Verifica que se ha llamado a all al menos una vez

    # Verificar que los motivos obtenidos son los mismos que los motivos existentes
    assert motivos == motivos_existentes

    # Verificar que los atributos de los usuarios son correctos
    for i, motivo in enumerate(motivos):
        assert motivo.id_motivo == motivos_existentes[i].id_motivo
        assert motivo.nombre_motivo == motivos_existentes[i].nombre_motivo

def test_retreive_motivo (mock_db):
    """Prueba unitaria de retreive_motivo con mocks"""
    # Datos de prueba:
    motivo_existente = TipoMotivo(id_motivo=1, nombre_motivo="Cambio de rol")
    id = 1

    # Mock del query para retornar el motivo existente
    mock_db.query().filter().first.return_value = motivo_existente

    # Llamar a la función bajo prueba
    motivo = retreive_motivo(id, mock_db)

    #Verificaciones
    mock_db.query().filter().first.assert_called_once() # Verifica que se ha llamado a all al menos una vez

    # Verificar que el usuario obtenido es el existente
    assert motivo == motivo_existente

    # Verificar que los atributos del usuario obtenido son los del existente
    assert motivo.id_motivo == motivo_existente.id_motivo
    assert motivo.nombre_motivo == motivo_existente.nombre_motivo
