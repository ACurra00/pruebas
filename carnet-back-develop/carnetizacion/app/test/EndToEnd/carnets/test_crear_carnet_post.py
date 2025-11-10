from db.models.registro import Registro

from datetime import datetime
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
from main import app  # Asegúrate de que el path sea correcto
from db.models.usuario import Usuario
import requests
from db.models.carnet_activo import CarnetActivo
from db.models.person import Person
from fastapi import Request
from pydantic import BaseModel
from db.models.carnet_activo import estado

class DummySession:
    def close(self):
        pass

def override_get_db() -> Session:
    return DummySession()

# Sobrescribe las dependencias get_db y get_db_roles
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_roles] = override_get_db

class DummyCrearCarnetForm:
    def __init__(self, request: Request):
        self.folio_desactivo = "123"
        self.rol_anterior = "Seminterno"
        self.area_anterior = "Facultad de Ingenieria Informatica"
        self.annoEstudiantePersona = "5"
        self.nombre = "Enmanuel de Jesus Santamaria Diaz"
        self.ci = "02032466727"
        self.comprobante_motivo = "A"
        self.tipoPersona = "Estudiante"
        self.area = "Facultad de Ingenieria Informatica"
        self.tipoMotivo = "Cambio de rol"
        self.rol = "Seminterno"
        self.errorFolio = ""
        self.errorMotivo = ""

    async def load_data(self):
        """Simula la carga de datos (no hace nada porque ya están fijos)."""
        pass

    async def is_valid(self):
        """Simula la validación de datos."""
        if not self.tipoMotivo or self.tipoMotivo == "Seleccione":
            self.errorMotivo = "Un motivo es requerido"
        return not self.errorFolio and not self.errorMotivo

class DummyCarnetActivoCreate(BaseModel):
    folio: int
    comprobante_motivo: str
    estado: str = "Solicitado"
    fecha: datetime = datetime.now()

#Crea bien los carnets:
@pytest.mark.asyncio
async def test_crear_carnet_post_success(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    async def dummy_form():
        return DummyCrearCarnetForm()  # Simula los datos que request.form() devolvería

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    # Simulación de funciones necesarias para la lógica interna
    def dummy_buscarAreas():
        return [  {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Electrica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Electrica"
       }    ,
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Industrial,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Industrial"
      },
      {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Informatica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
      "name": "Facultad de Ingenieria Informatica"
      },
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Mecanica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
       "name": "Facultad de Ingenieria Mecanica"
       }]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_buscarTrabajdor_and_Estudiante(ci, areatemp):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5",
                 "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que no tiene carnet previo

    def dummy_create_new_person(person_data, db):
        return Person(ci="02032466727", nombre="Enmanuel de Jesus Santamaria Diaz",
                               is_activa = True, area = "Facultad de Ingenieria Informatica",
                              rol = "Seminterno")  # Simula creación exitosa de persona

    def dummy_create_new_carnet_activo(carnet_activo, db, person_ci, tipo_motivo_id):
        return CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                                           comprobante_motivo="A", estado="Solicitado", fecha=datetime(2025, 2, 17))  # Simula creación exitosa del carnet

    def dummy_buscar_Tipo_Estudiante_carnet(ci: str):
        """Simula la búsqueda del tipo de estudiante sin hacer una solicitud real."""
        return "Seminterno"

    def dummy_buscar_trabajador_con_cargo(ci: str, get_db_roles):
        return False

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

        # Parches para reemplazar funciones reales por versiones simuladas
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.crearCarnetForm", DummyCrearCarnetForm)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.CarnetActivoCreate", DummyCarnetActivoCreate)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_person", dummy_create_new_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_carnet_activo", dummy_create_new_carnet_activo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_registro", dummy_create_new_registro)

    # Parámetros de entrada simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/crear_carnet/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 302  # Redirección exitosa
    assert response.headers["location"] == "/carnets/solicitados"  # Verifica que redirige al lugar correcto

#No esta logueado y redirecciona al login pq el token no es valido
@pytest.mark.asyncio
async def test_crear_carnet_post_fail_invalid_token(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    async def dummy_form():
        return DummyCrearCarnetForm()  # Simula los datos que request.form() devolvería

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    # Simulación de funciones necesarias para la lógica interna
    def dummy_buscarAreas():
        return [  {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Electrica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Electrica"
       }    ,
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Industrial,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Industrial"
      },
      {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Informatica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
      "name": "Facultad de Ingenieria Informatica"
      },
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Mecanica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
       "name": "Facultad de Ingenieria Mecanica"
       }]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_buscarTrabajdor_and_Estudiante(ci, areatemp):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5",
                 "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que no tiene carnet previo

    def dummy_create_new_person(person_data, db):
        return Person(ci="02032466727", nombre="Enmanuel de Jesus Santamaria Diaz",
                               is_activa = True, area = "Facultad de Ingenieria Informatica",
                              rol = "Seminterno")  # Simula creación exitosa de persona

    def dummy_create_new_carnet_activo(carnet_activo, db, person_ci, tipo_motivo_id):
        return CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                                           comprobante_motivo="A", estado="Solicitado", fecha=datetime(2025, 2, 17))  # Simula creación exitosa del carnet

    def dummy_buscar_Tipo_Estudiante_carnet(ci: str):
        """Simula la búsqueda del tipo de estudiante sin hacer una solicitud real."""
        return "Seminterno"

    def dummy_buscar_trabajador_con_cargo(ci: str, get_db_roles):
        return False

        # Parches para reemplazar funciones reales por versiones simuladas
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.crearCarnetForm", DummyCrearCarnetForm)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.CarnetActivoCreate", DummyCarnetActivoCreate)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_person", dummy_create_new_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_carnet_activo", dummy_create_new_carnet_activo)

    # Parámetros de entrada simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/crear_carnet/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 302  # Redirección exitosa
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

#Falla la conexion y muestra el error:
@pytest.mark.asyncio
async def test_crear_carnet_post_invalid_token(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    async def dummy_form():
        return DummyCrearCarnetForm()  # Simula los datos que request.form() devolvería

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    # Simulación de funciones necesarias para la lógica interna
    def dummy_buscarAreas():
        return [  {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Electrica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Electrica"
       }    ,
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Industrial,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
        "name": "Facultad de Ingenieria Industrial"
      },
      {
       "distinguishedName": "OU\u003dFacultad de Ingenieria Informatica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
      "name": "Facultad de Ingenieria Informatica"
      },
       {
        "distinguishedName": "OU\u003dFacultad de Ingenieria Mecanica,DC\u003dcujae,DC\u003dedu,DC\u003dcu",
       "name": "Facultad de Ingenieria Mecanica"
       }]

    def dummy_buscarAreas_por_name(areas, area):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_buscarTrabajdor_and_Estudiante(ci, areatemp):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5",
                 "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que no tiene carnet previo

    def dummy_create_new_person(person_data, db):
        return Person(ci="02032466727", nombre="Enmanuel de Jesus Santamaria Diaz",
                               is_activa = True, area = "Facultad de Ingenieria Informatica",
                              rol = "Seminterno")  # Simula creación exitosa de persona

    def dummy_create_new_carnet_activo(carnet_activo, db, person_ci, tipo_motivo_id):
        return CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                                           comprobante_motivo="A", estado="Solicitado", fecha=datetime(2025, 2, 17))  # Simula creación exitosa del carnet

    def dummy_buscar_Tipo_Estudiante_carnet(ci: str):
        """Simula la búsqueda del tipo de estudiante sin hacer una solicitud real."""
        return "Seminterno"

    def dummy_buscar_trabajador_con_cargo(ci: str, get_db_roles):
        return False

        # Parches para reemplazar funciones reales por versiones simuladas
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.crearCarnetForm", DummyCrearCarnetForm)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.CarnetActivoCreate", DummyCarnetActivoCreate)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_person", dummy_create_new_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_carnet.create_new_carnet_activo", dummy_create_new_carnet_activo)

    # Parámetros de entrada simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/crear_carnet/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 503  # Redirección exitosa
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

