import os
import zipfile
from collections import namedtuple
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from db.session import get_db
from db.session import get_db_roles
from sqlalchemy.orm import Session
from db.models.usuario import Usuario
from webapp.home.router_home import carnet_por_lotes
from main import app  # Asegúrate de que el path sea correcto
from db.models.usuario import Usuario
import requests
from pydantic import BaseModel
from db.models.carnet_activo import CarnetActivo
from db.models.person import Person
from unittest.mock import patch

#client = TestClient(app)

# Mocks de funciones dependientes
from db.models.registro import Registro

DUMMY_CARNET = [MagicMock()]
DUMMY_CARNET[0].Person.rol = "Seminterno"
DUMMY_CARNET[0].CarnetActivo.person_ci = "12345678"

DUMMY_USER = {"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "5",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}
DUMMY_PDF = b"dummy pdf content"  # Simula el contenido de un PDF

# Mock para la sesión de la base de datos
class DummySession:
    def close(self):
        pass

def override_get_db() -> Session:
    return DummySession()

# Sobrescribe las dependencias get_db y get_db_roles
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_roles] = override_get_db

# Sobrescribir la función get_carnet_by_ci
# Crear un objeto mock para Person

@pytest.mark.asyncio
async def test_imprimir_foto_success(monkeypatch):
    from api.endpoints.router_imprimir_carnet import print_carnets_solicitado

    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")
    carnet_id = "02032466727"
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    DUMMY_CARNET_RESPONSE = [DummyRow(
        CarnetActivo(id=1, person_ci=carnet_id, folio=1, tipo_motivo_id=1,
                     comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
        Person(ci=carnet_id, nombre="Sandro Rodriguez", is_activa=True,
               area="Facultad de Ingenieria Informatica", rol="Seminterno")
    )]

    def dummy_get_carnet_by_ci(db, carnet_id):
        return DUMMY_CARNET_RESPONSE

    def override_crear_imagen(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), 'cujae.png')

    def override_buscar_personas_por_ci(ci):
        return [DUMMY_USER]

    def override_buscarTrabajdor_and_Estudiante(ci):
        return [DUMMY_USER]

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.get_carnet_by_ci", dummy_get_carnet_by_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_imagen", override_crear_imagen)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante", override_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.create_new_registro", dummy_create_new_registro)

    response = print_carnets_solicitado(db=MagicMock(), current_user=usuario_autenticado_token, carnet_id=carnet_id)

    assert hasattr(response, "body_iterator"), "La respuesta no es un streaming"
    assert response.media_type == "application/x-zip-compressed"
    assert "attachment;filename=" in response.headers["Content-Disposition"]

    zip_bytes = b"".join([chunk async for chunk in response.body_iterator])
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zip_file:
        file_list = zip_file.namelist()
        assert len(file_list) > 0
        assert file_list[0].endswith(".png")

DUMMY_CARNET_LIST = [MagicMock()]


@pytest.mark.asyncio
async def test_print_carnets_solicitados_por_tipo(monkeypatch):
    from api.endpoints.router_imprimir_carnet import print_carnets_solicitados_por_tipo
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")
    carnet_id = "02032466727"
    # Simulación de los datos Dummy para el carnet
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    dummy_carnet = DummyRow(
        CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                     comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
        Person(ci="02032466727", nombre="Sandro Rodriguez",
               is_activa=True, area="Facultad de Ingenieria Informatica", rol="Seminterno")
    )

    DUMMY_CARNET_RESPONSE = [DummyRow(
        CarnetActivo(id=1, person_ci=carnet_id, folio=1, tipo_motivo_id=1,
                     comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
        Person(ci=carnet_id, nombre="Sandro Rodriguez", is_activa=True,
               area="Facultad de Ingenieria Informatica", rol="Seminterno")
    )]

    def dummy_get_carnet_by_ci(db, carnet_id):
        return DUMMY_CARNET_RESPONSE


    def override_crear_pdf(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), 'Estudiante Seminterno-fecha_ 2024-09-03.pdf')
    def override_buscar_personas_por_ci(ci):
        return [DUMMY_USER]

    def override_buscarTrabajdor_and_Estudiante(ci):
        return [DUMMY_USER]

    def dummy_lista_solicitados(db):
        return []

    def dummy_lista_solicitados_docente(db):
        return []

    def dummy_lista_solicitados_no_docente(db):
        return []


    def dummy_lista_solicitados_becado(db):
        return []

    def dummy_lista_solicitados_becado_ex(db):
        return []

    def dummy_lista_solicitados_ex(db):
        return []

    def dummy_lista_solicitados_cuadros(db):
        return []

    def dummy_lista_solicitados_seminterno(db):
        return [
            DummyRow(
                CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="02032466727", nombre="Sandro Rodriguez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            ),
            DummyRow(
                CarnetActivo(id=1, person_ci="01032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="01032466727", nombre="Sandro Gomez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            )
        ]

    def dummy_lista_solicitados_consejo(db):
        return []

    def dummy_lista_solicitados_externo(db):
        return []
    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    # Creando las listas de mock para las solicitudes
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados", dummy_lista_solicitados)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_docente", dummy_lista_solicitados_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_no_docente", dummy_lista_solicitados_no_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_seminterno", dummy_lista_solicitados_seminterno)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado", dummy_lista_solicitados_becado)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado_ex", dummy_lista_solicitados_becado_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_ex", dummy_lista_solicitados_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_cuadros", dummy_lista_solicitados_cuadros)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_consejo", dummy_lista_solicitados_consejo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_externo", dummy_lista_solicitados_externo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante", override_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_pdf", override_crear_pdf)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.create_new_registro", dummy_create_new_registro)

    # Llamada a la función del endpoint
    response = print_carnets_solicitados_por_tipo(db=MagicMock(), current_user=usuario_autenticado_token)

    # Verificaciones de la respuesta
    assert hasattr(response, "body_iterator"), "La respuesta no es un streaming"
    assert response.media_type == "application/x-zip-compressed"
    assert "attachment;filename=" in response.headers["Content-Disposition"]

    # Leer los archivos del ZIP en la respuesta
    zip_bytes = b"".join([chunk async for chunk in response.body_iterator])
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zip_file:
        file_list = zip_file.namelist()
        # Verificar que el ZIP contiene archivos PDF
        assert any(f.endswith(".pdf") for f in file_list)
@pytest.mark.asyncio
async def test_imprimir_fotos_success(monkeypatch):
    from api.endpoints.router_imprimir_carnet import print_carnets_solicitados_por_tipo_fotos
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    dummy_carnet = DummyRow(
        CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                     comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
        Person(ci="02032466727", nombre="Sandro Rodriguez",
               is_activa=True, area="Facultad de Ingenieria Informatica", rol="Seminterno")
    )

    def dummy_lista_solicitados(db):
        return []

    def dummy_lista_solicitados_docente(db):
        return []

    def dummy_lista_solicitados_no_docente(db):
        return []

    def dummy_lista_solicitados_seminterno(db):
        return [
            DummyRow(
                CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="02032466727", nombre="Sandro Rodriguez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            )]

    def dummy_lista_solicitados_becado(db):
        return []

    def dummy_lista_solicitados_becado_ex(db):
        return []

    def dummy_lista_solicitados_ex(db):
        return []

    def dummy_lista_solicitados_cuadros(db):
        return []

    def dummy_lista_solicitados_consejo(db):
        return []

    def dummy_lista_solicitados_externo(db):
        return []

    def override_buscarTrabajdor_and_Estudiante(ci):
        return [DUMMY_USER]  # Devuelve un usuario ficticio

    def override_buscar_personas_por_ci(ci):
        return [DUMMY_USER]  # Devuelve un usuario ficticio

    # Mock de la función get_carnet_by_ci
    carnet_id = "02032466727"

    # Sobrescribir la función crear_imagen
    def override_crear_imagen(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), 'cujae.png')  # Devuelve el contenido simulado del PDF

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    # Sobrescribir la función buscar_personas_por_ci

    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados", dummy_lista_solicitados)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_docente",
                        dummy_lista_solicitados_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_no_docente",
                        dummy_lista_solicitados_no_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_seminterno",
                        dummy_lista_solicitados_seminterno)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado", dummy_lista_solicitados_becado)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado_ex",
                        dummy_lista_solicitados_becado_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_ex", dummy_lista_solicitados_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_cuadros",
                        dummy_lista_solicitados_cuadros)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_consejo",
                        dummy_lista_solicitados_consejo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_externo",
                        dummy_lista_solicitados_externo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_imagen", override_crear_imagen)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante",
                        override_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.create_new_registro", dummy_create_new_registro)

    response = print_carnets_solicitados_por_tipo_fotos(db=MagicMock(), current_user=usuario_autenticado_token)

    assert hasattr(response, "body_iterator")
    assert response.media_type == "application/x-zip-compressed"
    assert "attachment;filename=" in response.headers["Content-Disposition"]

    zip_bytes = b"".join([chunk async for chunk in response.body_iterator])
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zip_file:
        file_list = zip_file.namelist()
        assert any(f.endswith(".png") for f in file_list)

@pytest.mark.asyncio
async def test_imprimir_fail_conection (monkeypatch):

    # Retorno simulado de get_carnet_by_ci (debe ser una lista de tuplas)
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    DUMMY_CARNET_RESPONSE = [DummyRow(
        CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                     comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
        Person(ci="02032466727", nombre="Sandro Rodriguez",
               is_activa=True, area="Facultad de Ingenieria Informatica",
               rol="Seminterno")
    )]

    # Mock de la función get_carnet_by_ci
    carnet_id = "02032466727"

    def dummy_get_carnet_by_ci(db, carnet_id):
        return DUMMY_CARNET_RESPONSE  # Devuelve el mock

    # Sobrescribir la función crear_imagen
    def override_crear_imagen(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), 'cujae.png')  # Devuelve el contenido simulado del PDF

    # Sobrescribir la función buscar_personas_por_ci
    def override_buscar_personas_por_ci(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

    # Sobrescribir la función buscarTrabajdor_and_Estudiante
    def override_buscarTrabajdor_and_Estudiante(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.get_carnet_by_ci", dummy_get_carnet_by_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_imagen", override_crear_imagen)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante", override_buscarTrabajdor_and_Estudiante)


    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/imprimir_carnets_solicitados", params={"carnet_id": carnet_id})

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_imprimir_fotos_fail_connection(monkeypatch):

    # Retorno simulado de get_carnet_by_ci (debe ser una lista de tuplas)
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    def dummy_lista_solicitados(db):
        return []

    def dummy_lista_solicitados_docente(db):
        return []

    def dummy_lista_solicitados_no_docente(db):
        return []

    def dummy_lista_solicitados_seminterno(db):
        return [
            DummyRow(
                CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="02032466727", nombre="Sandro Rodriguez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            )]

    def dummy_lista_solicitados_becado(db):
        return []

    def dummy_lista_solicitados_becado_ex(db):
        return []

    def dummy_lista_solicitados_ex(db):
        return []

    def dummy_lista_solicitados_cuadros(db):
        return []

    def dummy_lista_solicitados_consejo(db):
        return []

    def dummy_lista_solicitados_externo(db):
        return []

    def override_buscar_personas_por_ci(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

    # Sobrescribir la función buscarTrabajdor_and_Estudiante
    def override_buscarTrabajdor_and_Estudiante(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

    # Mock de la función get_carnet_by_ci
    carnet_id = "02032466727"


    # Sobrescribir la función crear_imagen
    def override_crear_imagen(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), 'cujae.png')  # Devuelve el contenido simulado del PDF

    # Sobrescribir la función buscar_personas_por_ci


    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados", dummy_lista_solicitados)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_docente", dummy_lista_solicitados_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_no_docente", dummy_lista_solicitados_no_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_seminterno", dummy_lista_solicitados_seminterno)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado", dummy_lista_solicitados_becado)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado_ex", dummy_lista_solicitados_becado_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_ex", dummy_lista_solicitados_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_cuadros", dummy_lista_solicitados_cuadros)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_consejo", dummy_lista_solicitados_consejo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_externo", dummy_lista_solicitados_externo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_imagen", override_crear_imagen)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante", override_buscarTrabajdor_and_Estudiante)


    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(f"/imprimir_carnets_solicitados_por_tipos_fotos")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_print_carnets_solicitados_por_tipo_fail_connection(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo", "Person"])

    def dummy_lista_solicitados(db):
        return []

    def dummy_lista_solicitados_docente(db):
        return []

    def dummy_lista_solicitados_no_docente(db):
        return []

    def dummy_lista_solicitados_seminterno(db):
        return [
            DummyRow(
                CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="02032466727", nombre="Sandro Rodriguez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            ),
            DummyRow(
                CarnetActivo(id=1, person_ci="01032466727", folio=1, tipo_motivo_id=1,
                             comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17)),
                Person(ci="01032466727", nombre="Sandro Gomez",
                       is_activa=True, area="Facultad de Ingenieria Informatica",
                       rol="Seminterno")
            )
        ]

    def dummy_lista_solicitados_becado(db):
        return []

    def dummy_lista_solicitados_becado_ex(db):
        return []

    def dummy_lista_solicitados_ex(db):
        return []

    def dummy_lista_solicitados_cuadros(db):
        return []

    def dummy_lista_solicitados_consejo(db):
        return []

    def dummy_lista_solicitados_externo(db):
        return []

    def override_buscar_personas_por_ci(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

    # Sobrescribir la función buscarTrabajdor_and_Estudiante
    def override_buscarTrabajdor_and_Estudiante(ci):
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    def dummy_crear_pdf(list, folio, nombre, db):
        return os.path.join(os.path.dirname(__file__), f"Estudiante Seminterno-fecha_ 2024-09-03.pdf")

    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados", dummy_lista_solicitados)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_docente", dummy_lista_solicitados_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_no_docente", dummy_lista_solicitados_no_docente)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_seminterno", dummy_lista_solicitados_seminterno)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado", dummy_lista_solicitados_becado)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_becado_ex", dummy_lista_solicitados_becado_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_ex", dummy_lista_solicitados_ex)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_cuadros", dummy_lista_solicitados_cuadros)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_consejo", dummy_lista_solicitados_consejo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.lista_solicitados_externo", dummy_lista_solicitados_externo)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscar_personas_por_ci", override_buscar_personas_por_ci)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.buscarTrabajdor_and_Estudiante", override_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("api.endpoints.router_imprimir_carnet.crear_pdf", dummy_crear_pdf)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/imprimir_carnets_solicitados_por_tipos")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."