from unittest.mock import MagicMock
import pytest
from sqlalchemy.orm import Session
from db.models.carnet_activo import CarnetActivo
from schemas.person import PersonCreate
from db.models.person import Person
from db.repository.person import create_new_person, retreive_person, list_personas_por_ci, list_personas_por_area, list_personas_por_area_tipo, list_personas_por_nombre, list_personas_por_todos, update_person_by_ci

@pytest.fixture
def mock_db():
    """Mock de la sesión de la base de datos"""
    mock_session = MagicMock()
    return mock_session

def test_create_new_person(mock_db):
    """Prueba unitaria de create_new_person con mocks"""

    # Datos de prueba
    person_data = carnet_data = PersonCreate(ci="02032466727",
                                     nombre="Saul Rodriguez",
                                     area = "Facultad de Ingenieria Informatica",
                                     rol = "Seminterno")

    # Mock del usuario para evitar acceso a la BD real
    mock_person = Person(**person_data.dict())
    mock_db.add.return_value = None  # `add` no devuelve nada
    mock_db.commit.return_value = None  # `commit` no devuelve nada
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)  # Simula asignar un ID

    # Llamar a la función bajo prueba
    new_person = create_new_person(person_data, mock_db)

    # Verificaciones
    mock_db.add.assert_called_once()  # Verifica que `add
    # Verificar que los atributos sean iguales (comparación por valor, no referencia)
    added_person= mock_db.add.call_args[0][0]
    assert added_person.ci == person_data.ci
    assert added_person.nombre == person_data.nombre
    assert added_person.area == person_data.area
    assert added_person.rol == person_data.rol
    mock_db.commit.assert_called_once() # Verifica que commit
    mock_db.refresh.assert_called_once_with(added_person)  # `refresh` debe haberse llamado con el usuario

    # Verifica que los datos sean los correctos
    assert new_person.id == 1  # Simulación de ID asignado
    assert new_person.ci == "02032466727"
    assert new_person.nombre == "Saul Rodriguez"
    assert new_person.area == "Facultad de Ingenieria Informatica"
    assert new_person.rol == "Seminterno"

def test_update_person_by_ci(mock_db):
    """Prueba unitaria de update_person_by_ci con mocks"""

    # Datos de prueba
    person_data = PersonCreate(ci="02032466727",
                                     nombre="Saul Rodriguez",
                                     area = "Facultad de Ingenieria Informatica",
                                     rol = "Becado Nacional")
    exist_person = Person(ci="02032466727", nombre="Sandro Rodriguez",
                               is_activa = True, area = "Facultad de Ingenieria Informatica",
                              rol = "Becado Nacional")

    # Mock del motivo existente para evitar acceso a la BD real
    mock_db.query().filter().first.return_value = exist_person
    mock_db.commit.return_value = None  # `commit` no devuelve nada

    # Llamar a la función bajo prueba
    result = update_person_by_ci("02032466727", person_data, mock_db)

    # Verificaciones
    mock_db.query().filter().first.assert_called_once()  # Verifica que se ha llamado a `filter` una vez
    mock_db.commit.assert_called_once()  # Verifica que `commit` se ha llamado una vez
    mock_db.query().filter().update.assert_called_once_with(person_data.__dict__)  # Verifica que `update` se ha llamado con los datos correctos

    # Verifica que el resultado sea el esperado
    assert result == 1

def test_retreive_person (mock_db):
    """Prueba unitaria de retreive_person con mocks"""
    # Datos de prueba:
    persona_existente = Person(ci="02032466727", nombre="Sandro Rodriguez",
                               is_activa = True, area = "Facultad de Ingenieria Informatica",
                              rol = "Seminterno")

    ci="02032466727"

    # Mock del query para retornar la persona existente
    mock_db.query().filter().first.return_value = persona_existente

    # Llamar a la función bajo prueba
    persona = retreive_person(ci, mock_db)

    #Verificaciones
    mock_db.query().filter().first.assert_called_once() # Verifica que se ha llamado a all al menos una vez

    # Verificar que el usuario obtenido es el existente
    assert persona == persona_existente

    # Verificar que los atributos del usuario obtenido son los del existente
    assert persona.ci == persona_existente.ci
    assert persona.nombre == persona_existente.nombre
    assert persona.is_activa == persona_existente.is_activa
    assert persona.area == persona_existente.area
    assert persona.rol == persona_existente.rol


def test_list_personas_por_area(mock_db):
    """Prueba unitaria de list_personas_por_area con mocks"""

    # Datos de prueba
    personas_existentes = [
        Person(ci="02032466727", nombre="Sandro Rodriguez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Seminterno"),
        Person(ci="03032466888", nombre="Maria Perez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Profesor"),
        Person(ci="04032466999", nombre="Juan Gomez", is_activa=False, area="Facultad de Ingenieria Mecanica", rol="Estudiante")
    ]

    # Configurar el mock para retornar la lista de personas según el área
    mock_query = MagicMock()
    mock_query.filter.return_value = [personas_existentes[0], personas_existentes[1]]
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    personas = list_personas_por_area(mock_db, "Facultad de Ingenieria Informatica")

    # Verificaciones
    mock_db.query.assert_called_once_with(Person)  # Verifica que se ha llamado a query con el modelo Person
    mock_query.filter.assert_called_once()  # Verifica que se ha llamado a filter con el área correcta

    # Verificar que las personas obtenidas son las mismas que las personas existentes en el área
    assert personas == [personas_existentes[0], personas_existentes[1]]

    # Verificar que las personas obtenidas son las mismas que las personas existentes en el área
    assert len(personas) == 2  # Verifica que solo se han obtenido dos personas
    assert personas[0].ci == personas_existentes[0].ci
    assert personas[0].nombre == personas_existentes[0].nombre
    assert personas[0].is_activa == personas_existentes[0].is_activa
    assert personas[0].area == personas_existentes[0].area
    assert personas[0].rol == personas_existentes[0].rol

    assert personas[1].ci == personas_existentes[1].ci
    assert personas[1].nombre == personas_existentes[1].nombre
    assert personas[1].is_activa == personas_existentes[1].is_activa
    assert personas[1].area == personas_existentes[1].area
    assert personas[1].rol == personas_existentes[1].rol

def test_list_personas_por_ci(mock_db):
    """Prueba unitaria de list_personas_por_ci con mocks"""

    # Datos de prueba
    personas_existentes = [
        Person(ci="02032466727", nombre="Sandro Rodriguez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Seminterno"),
        Person(ci="02032466728", nombre="Maria Perez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Profesor"),
        Person(ci="04032466999", nombre="Juan Gomez", is_activa=False, area="Facultad de Ingenieria Mecanica", rol="Estudiante")
    ]

    # Configurar el mock para retornar la lista de personas según el CI
    mock_query = MagicMock()
    mock_query.filter.return_value = [personas_existentes[0]]
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    personas = list_personas_por_ci(mock_db, "02032466727")

    # Verificaciones
    mock_db.query.assert_called_once_with(Person)  # Verifica que se ha llamado a query con el modelo Person
    mock_query.filter.assert_called_once()

    # Verificar que las personas obtenidas son las mismas que las personas existentes con el ci
    assert personas == [personas_existentes[0]]

    # Verificar que las personas obtenidas son las mismas que las personas existentes con el ci
    assert len(personas) == 1  # Verifica que solo se han obtenido dos personas
    assert personas[0].ci == personas_existentes[0].ci
    assert personas[0].nombre == personas_existentes[0].nombre
    assert personas[0].is_activa == personas_existentes[0].is_activa
    assert personas[0].area == personas_existentes[0].area
    assert personas[0].rol == personas_existentes[0].rol

def test_list_personas_por_nombre (mock_db):
    """Prueba unitaria de list_personas_por_nombre con mocks"""

    # Datos de prueba
    personas_existentes = [
        Person(ci="02032466727", nombre="Sandro Rodriguez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Seminterno"),
        Person(ci="02032466728", nombre="Maria Perez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Profesor"),
        Person(ci="04032466999", nombre="Juan Gomez", is_activa=False, area="Facultad de Ingenieria Mecanica", rol="Estudiante")
    ]

    # Configurar el mock para retornar la lista de personas según el CI
    mock_query = MagicMock()
    mock_query.filter.return_value = [personas_existentes[0]]
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    personas = list_personas_por_nombre(mock_db, "Sandro Rodriguez")

    # Verificaciones
    mock_db.query.assert_called_once_with(Person)  # Verifica que se ha llamado a query con el modelo Person
    mock_query.filter.assert_called_once()

    # Verificar que la persona obtenida es la correcta
    assert personas == [personas_existentes[0]]

    # Verificar que los atributos son correctos
    assert len(personas) == 1  # Verifica que solo se han obtenido dos personas
    assert personas[0].ci == personas_existentes[0].ci
    assert personas[0].nombre == personas_existentes[0].nombre
    assert personas[0].is_activa == personas_existentes[0].is_activa
    assert personas[0].area == personas_existentes[0].area
    assert personas[0].rol == personas_existentes[0].rol

def test_list_personas_por_area_tipo (mock_db):
    """Prueba unitaria de list_personas_por_area_tipo con mocks"""

    # Datos de prueba
    personas_existentes = [
        Person(ci="02032466727", nombre="Sandro Rodriguez", is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Seminterno"),
        Person(ci="02032466728", nombre="Maria Perez", is_activa=True, area="Facultad de Ingenieria Mecanica",
               rol="Becado"),
        Person(ci="04032466999", nombre="Juan Gomez", is_activa=False, area="Facultad de Ingenieria Informatica", rol="Seminterno")
    ]

    # Configurar el mock para retornar la lista de personas según el CI
    mock_query = MagicMock()
    mock_query.filter.return_value = [personas_existentes[0], personas_existentes[2]]
    mock_db.query.return_value = mock_query

    # Llamar a la función bajo prueba
    personas = list_personas_por_area_tipo(mock_db, "Facultad de Ingenieria Informatica", "Seminterno")

    # Verificaciones
    mock_db.query.assert_called_once_with(Person)  # Verifica que se ha llamado a query con el modelo Person
    mock_query.filter.assert_called_once()

    # Verificar que la persona obtenida es la correcta
    assert personas == [personas_existentes[0], personas_existentes[2]]

    # Verificar que los atributos son correctos
    assert len(personas) == 2  # Verifica que solo se han obtenido dos personas
    assert personas[0].ci == personas_existentes[0].ci
    assert personas[0].nombre == personas_existentes[0].nombre
    assert personas[0].is_activa == personas_existentes[0].is_activa
    assert personas[0].area == personas_existentes[0].area
    assert personas[0].rol == personas_existentes[0].rol

    assert personas[1].ci == personas_existentes[2].ci
    assert personas[1].nombre == personas_existentes[2].nombre
    assert personas[1].is_activa == personas_existentes[2].is_activa
    assert personas[1].area == personas_existentes[2].area
    assert personas[1].rol == personas_existentes[2].rol

