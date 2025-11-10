import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from schemas.carnet_activo import CarnetActivoCreate
from db.models.carnet_activo import CarnetActivo
from db.repository.carnet_activo import create_new_carnet_activo, update_carnetactivo_by_ci, retreive_carnet
from db.repository.carnet_activo import lista_carnet_activo_x_ci, lista_carnet_activo_x_nombre, cambiar_estado
from db.models.person import Person
from sqlalchemy import select
from datetime import datetime

@pytest.fixture
def mock_db():
    """Mock de la sesión de la base de datos"""
    mock_session = MagicMock()
    return mock_session

def test_create_new_carnet_activo(mock_db):
    """Prueba unitaria de create_new_carnet_activo con mocks"""

    # Datos de prueba
    estado = "Solicitado"
    carnet_data = CarnetActivoCreate(folio=4056,
                                     comprobante_motivo="ok",
                                     estado = estado,
                                     fecha = datetime.now())
    person_ci = 0o2032466727
    tipo_motivo_id = 24
    # Mock del usuario para evitar acceso a la BD real
    mock_carnet = CarnetActivo(**carnet_data.dict(),person_ci=person_ci, tipo_motivo_id= tipo_motivo_id)
    mock_db.add.return_value = None  # `add` no devuelve nada
    mock_db.commit.return_value = None  # `commit` no devuelve nada
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)  # Simula asignar un ID

    # Llamar a la función bajo prueba
    new_carnet = create_new_carnet_activo(carnet_data, mock_db, person_ci, tipo_motivo_id)

    # Verificaciones
    mock_db.add.assert_called_once()  # Verifica que `add
    # Verificar que los atributos sean iguales (comparación por valor, no referencia)
    added_carnet = mock_db.add.call_args[0][0]
    assert added_carnet.folio == carnet_data.folio
    assert added_carnet.comprobante_motivo == carnet_data.comprobante_motivo  #
    assert added_carnet.estado == carnet_data.estado
    assert added_carnet.fecha == carnet_data.fecha
    mock_db.commit.assert_called_once() # Verifica que commit
    mock_db.refresh.assert_called_once_with(added_carnet)  # `refresh` debe haberse llamado con el usuario

    # Verifica que los datos sean los correctos
    assert new_carnet.id == 1  # Simulación de ID asignado
    assert new_carnet.folio == 4056
    assert new_carnet.comprobante_motivo == "ok"
    assert new_carnet.estado == estado


def test_update_carnetactivo_by_ci(mock_db):
    """Prueba unitaria de update_carnetactivo_by_ci con mocks"""

    # Datos de prueba
    carnet_activo_existente = CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                                           comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
    estado = "Solicitado"
    carnet_data = CarnetActivoCreate(folio=4098,
                                     comprobante_motivo="ok",
                                     estado=estado,
                                     fecha=datetime.now())

    # Configurar el mock para retornar el carnet activo existente
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = carnet_activo_existente
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    resultado = update_carnetactivo_by_ci("02032466727", carnet_data, mock_db)

    # Verificaciones
    mock_db.query.assert_called_once_with(CarnetActivo)
    mock_query.filter.assert_called_once()
    mock_query.update.assert_called_once()
    mock_db.commit.assert_called_once()

    # Verificar que la función retorna 1 (indica éxito)
    assert resultado == 1

    # Prueba cuando no existe el carnet activo
    mock_query.first.return_value = None
    resultado = update_carnetactivo_by_ci("02032466727", carnet_data, mock_db)
    assert resultado == 0

def test_retreive_carnet(mock_db):
    """Prueba unitaria de retreive_carnet con mocks"""

    # Datos de prueba
    carnet_activo = CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1, comprobante_motivo="A", estado="Activo", fecha=datetime(2025, 2, 17))

    # Configurar el mock para retornar el carnet activo
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = carnet_activo
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    item = retreive_carnet(1, mock_db)

    # Verificaciones
    mock_db.query.assert_called_once_with(CarnetActivo)
    mock_query.filter.assert_called_once()
    mock_query.first.assert_called_once()

    # Verificar que el item obtenido es el mismo que el carnet activo
    assert item == carnet_activo

def test_lista_carnet_activo_x_ci(mock_db):
    """Prueba unitaria de lista_carnet_activo_x_ci con mocks"""

    # Datos de prueba
    carnets_activos = [
        CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1, comprobante_motivo="A", estado="Activo", fecha=datetime(2025, 2, 17)),
        CarnetActivo(id=2, person_ci="02032466728", folio=2, tipo_motivo_id=1, comprobante_motivo="B", estado="Activo", fecha=datetime(2025, 2, 18))
    ]

    # Configurar el mock para retornar los carnets activos por CI
    mock_query = MagicMock()
    mock_filtered_query = MagicMock()
    mock_filtered_query.order_by.return_value = [carnets_activos[0]]
    mock_query.filter.return_value = mock_filtered_query
    mock_db.query.return_value = mock_query

    # Llamada de prueba
    carnets = lista_carnet_activo_x_ci(mock_db, "02032466727")

    # Verificaciones
    mock_db.query.assert_called_once_with(CarnetActivo)
    mock_query.filter.assert_called_once()
    mock_filtered_query.order_by.assert_called_once()

    # Verificar que los carnets obtenidos son los esperados
    assert carnets == [carnets_activos[0]]


def test_lista_carnet_activo_x_nombre(mock_db):
    """Prueba unitaria de lista_carnet_activo_x_nombre con mocks"""

    # Datos de prueba
    personas = [
        Person(ci="02032466727", nombre="Sandro Rodriguez"),
        Person(ci="03032466888", nombre="Maria Perez")
    ]
    carnets_activos = [
        CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1, comprobante_motivo="A", estado="Activo",
                     fecha=datetime(2025, 2, 17))
    ]

    # Configurar el mock para retornar los carnets activos por nombre
    mock_person_query = MagicMock()
    mock_filtered_person_query = MagicMock()
    mock_filtered_person_query.first.return_value = personas[0]
    mock_person_query.filter.return_value = mock_filtered_person_query
    mock_db.query.side_effect = [mock_person_query, mock_person_query]

    mock_carnet_query = MagicMock()
    mock_filtered_query = MagicMock()
    mock_filtered_query.order_by.return_value = carnets_activos
    mock_carnet_query.filter.return_value = mock_filtered_query
    mock_db.query.side_effect = [mock_carnet_query, mock_person_query]

    # Llamar a la función bajo prueba
    carnets = lista_carnet_activo_x_nombre(mock_db, "Sandro Rodriguez")

    # Verificaciones
    mock_db.query.assert_any_call(CarnetActivo)
    mock_db.query.assert_any_call(Person)
    mock_carnet_query.filter.assert_called_once()
    mock_filtered_query.order_by.assert_called_once()

    # Verificar que los carnets obtenidos son los esperados
    assert carnets == carnets_activos


def test_cambiar_estado(mock_db):
    """Prueba unitaria de cambiar_estado con mocks"""

    # Datos de prueba
    carnet_activo_existente = [CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                                           comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))]

    # Configurar el mock para retornar el carnet activo existente
    mock_query = MagicMock()
    mock_filtered_query = MagicMock()
    mock_filtered_query.first.return_value = carnet_activo_existente
    mock_query.filter.return_value = mock_filtered_query
    mock_db.query.return_value = mock_query
    mock_db.commit.return_value = None

    # Llamar a la función bajo prueba
    resultado = cambiar_estado(mock_db, "Entregado", "02032466727")

    mock_filtered_query.first.return_value = carnet_activo_actualizado
    mock_query.filter.return_value = mock_filtered_query
    mock_db.query.return_value = mock_query
    mock_db.commit.return_value = None

    # Verificaciones
    mock_db.query.assert_called_once_with(CarnetActivo)
    mock_filtered_query.update.assert_called_once()
    mock_db.commit.assert_called_once()

    # Verificar que la función retorna el carnet activo actualizado
    assert resultado == mock_filtered_query

