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

class DummyBuscarPersonaForm:
    def __init__(self, request: Request):
        self.ciBuscarPersona = "02032466727"
        self.areaBuscarPersona = "Facultad de Ingenieria Informatica"
        self.tipoBuscarPersona = "carnet_x_lotes_off"
        self.tipoBuscarCarnet = "carnet_x_lotes_Estudiante"
        self.users = [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "5",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]
        self.student_year = "5"
        self.errorCI = ""
        self.errorArea = ""
        self.errorTipo = ""
        self.errorFiltro = ""
        self.erroryear = ""

    async def load_data(self):
        """Simula la carga de datos (no hace nada porque ya están fijos)."""
        pass

    async def is_valid(self):
        """Simula la validación de datos."""
        result = True

        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False

        if self.tipoBuscarPersona == "carnet_x_lotes_off":  # No es por lotes
            if len(self.ciBuscarPersona) != 11:
                self.errorCI = "*Un Carnet de Identidad no válido"
                result = False
        elif self.tipoBuscarCarnet == "Seleccione":
            self.errorFiltro = "*Seleccione un elemento válido"
            self.erroryear = ""
            result = False

        if self.student_year == "Seleccione" and self.tipoBuscarCarnet == "carnet_x_lotes_Estudiante":
            self.errorFiltro = ""
            self.erroryear = "*Seleccione un elemento válido"
            result = False

        return result

    def is_carnet_x_lotes(self):
        """Simula la validación de si el carnet es por lotes."""
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
        if self.tipoBuscarPersona == "Seleccione":
            self.errorTipo = "*Este campo es obligatorio"
            result = False
        return result

class DummyBuscarPersonaFormLotesOn:
    def __init__(self, request: Request):
        self.ciBuscarPersona = "02032466727"
        self.areaBuscarPersona = "Facultad de Ingenieria Informatica"
        self.tipoBuscarPersona = "carnet_x_lotes_on"
        self.tipoBuscarCarnet = "carnet_x_lotes_Estudiante"
        self.users = [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "5",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]
        self.student_year = "5"
        self.errorCI = ""
        self.errorArea = ""
        self.errorTipo = ""
        self.errorFiltro = ""
        self.erroryear = ""

    async def load_data(self):
        """Simula la carga de datos (no hace nada porque ya están fijos)."""
        pass

    async def is_valid(self):
        """Simula la validación de datos."""
        result = True

        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False

        if self.tipoBuscarPersona == "carnet_x_lotes_off":  # No es por lotes
            if len(self.ciBuscarPersona) != 11:
                self.errorCI = "*Un Carnet de Identidad no válido"
                result = False
        elif self.tipoBuscarCarnet == "Seleccione":
            self.errorFiltro = "*Seleccione un elemento válido"
            self.erroryear = ""
            result = False

        if self.student_year == "Seleccione" and self.tipoBuscarCarnet == "carnet_x_lotes_Estudiante":
            self.errorFiltro = ""
            self.erroryear = "*Seleccione un elemento válido"
            result = False

        return result

    def is_carnet_x_lotes(self):
        """Simula la validación de si el carnet es por lotes."""
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
        if self.tipoBuscarPersona == "Seleccione":
            self.errorTipo = "*Este campo es obligatorio"
            result = False
        return result

@pytest.mark.asyncio
async def test_home_post_success_carnet_x_lotes_off(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "Ingeniería Mecánica (CPE)",
    "tipo_curso": "03",
    "facultad": "X0000"
    },
    {
    "idCarrera": "0000Y1",
    "nombre": "Ingeniería Química (CPE)",
    "tipo_curso": "03",
    "facultad": "Y0000"
    },
     {
    "idCarrera": "010901",
    "nombre": "Ingeniería Química (CED)",
    "tipo_curso": "05"
    },
    {
    "idCarrera": "010900",
    "nombre": "Ingeniería Química (CD)",
    "tipo_curso": "01",
    "facultad": "Y0000"
    },
    {
    "idCarrera": "-23a20229:123336a8d3c:-7de0",
    "nombre": "Ingeniería en Automática (CPE)",
    "tipo_curso": "03",
    "facultad": "R0000"
    },
    {
     "idCarrera": "010600",
    "nombre": "Ingeniería en Informatica (CD)",
    "tipo_curso": "01",
    "facultad": "R0000"
    },
    {
    "idCarrera": "010300",
    "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
    "tipo_curso": "01",
    "facultad": "X0000"
    }
    ]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_carnet_para_Persona(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm", DummyBuscarPersonaForm)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 200  # Debe devolver una respuesta exitosa


@pytest.mark.asyncio
async def test_home_post_success_carnet_x_lotes_off_person_not_found(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [

            {
                "idCarrera": "010401",
                "nombre": "Ingeniería Mecánica (CPE)",
                "tipo_curso": "03",
                "facultad": "X0000"
            },
            {
                "idCarrera": "0000Y1",
                "nombre": "Ingeniería Química (CPE)",
                "tipo_curso": "03",
                "facultad": "Y0000"
            },
            {
                "idCarrera": "010901",
                "nombre": "Ingeniería Química (CED)",
                "tipo_curso": "05"
            },
            {
                "idCarrera": "010900",
                "nombre": "Ingeniería Química (CD)",
                "tipo_curso": "01",
                "facultad": "Y0000"
            },
            {
                "idCarrera": "-23a20229:123336a8d3c:-7de0",
                "nombre": "Ingeniería en Automática (CPE)",
                "tipo_curso": "03",
                "facultad": "R0000"
            },
            {
                "idCarrera": "010600",
                "nombre": "Ingeniería en Informatica (CD)",
                "tipo_curso": "01",
                "facultad": "R0000"
            },
            {
                "idCarrera": "010300",
                "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
                "tipo_curso": "01",
                "facultad": "X0000"
            }
        ]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
        return (
        'Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
        'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
        ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
        'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
        'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
        ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),',
        42)

    def dummy_carnet_para_Persona(area, ci):
        return None

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return []

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm",DummyBuscarPersonaForm)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona",dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name",dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona",dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 200  # Debe devolver una respuesta exitosa
    assert "No se encontraró al estudiante en el área especificada" in response.text

@pytest.mark.asyncio
async def test_home_post_invalid_token(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "Ingeniería Mecánica (CPE)",
    "tipo_curso": "03",
    "facultad": "X0000"
    },
    {
    "idCarrera": "0000Y1",
    "nombre": "Ingeniería Química (CPE)",
    "tipo_curso": "03",
    "facultad": "Y0000"
    },
     {
    "idCarrera": "010901",
    "nombre": "Ingeniería Química (CED)",
    "tipo_curso": "05"
    },
    {
    "idCarrera": "010900",
    "nombre": "Ingeniería Química (CD)",
    "tipo_curso": "01",
    "facultad": "Y0000"
    },
    {
    "idCarrera": "-23a20229:123336a8d3c:-7de0",
    "nombre": "Ingeniería en Automática (CPE)",
    "tipo_curso": "03",
    "facultad": "R0000"
    },
    {
     "idCarrera": "010600",
    "nombre": "Ingeniería en Informatica (CD)",
    "tipo_curso": "01",
    "facultad": "R0000"
    },
    {
    "idCarrera": "010300",
    "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
    "tipo_curso": "01",
    "facultad": "X0000"
    }
    ]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_carnet_para_Persona(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm", DummyBuscarPersonaForm)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 302  # Debe devolver una respuesta exitosa
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_home_post_invalid_fail_connection(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "Ingeniería Mecánica (CPE)",
    "tipo_curso": "03",
    "facultad": "X0000"
    },
    {
    "idCarrera": "0000Y1",
    "nombre": "Ingeniería Química (CPE)",
    "tipo_curso": "03",
    "facultad": "Y0000"
    },
     {
    "idCarrera": "010901",
    "nombre": "Ingeniería Química (CED)",
    "tipo_curso": "05"
    },
    {
    "idCarrera": "010900",
    "nombre": "Ingeniería Química (CD)",
    "tipo_curso": "01",
    "facultad": "Y0000"
    },
    {
    "idCarrera": "-23a20229:123336a8d3c:-7de0",
    "nombre": "Ingeniería en Automática (CPE)",
    "tipo_curso": "03",
    "facultad": "R0000"
    },
    {
     "idCarrera": "010600",
    "nombre": "Ingeniería en Informatica (CD)",
    "tipo_curso": "01",
    "facultad": "R0000"
    },
    {
    "idCarrera": "010300",
    "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
    "tipo_curso": "01",
    "facultad": "X0000"
    }
    ]

    def dummy_buscarAreas_por_name(areas, area):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_carnet_para_Persona(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm", DummyBuscarPersonaForm)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_home_post_success_carnet_x_lotes_on(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "Ingeniería Mecánica (CPE)",
    "tipo_curso": "03",
    "facultad": "X0000"
    },
    {
    "idCarrera": "0000Y1",
    "nombre": "Ingeniería Química (CPE)",
    "tipo_curso": "03",
    "facultad": "Y0000"
    },
     {
    "idCarrera": "010901",
    "nombre": "Ingeniería Química (CED)",
    "tipo_curso": "05"
    },
    {
    "idCarrera": "010900",
    "nombre": "Ingeniería Química (CD)",
    "tipo_curso": "01",
    "facultad": "Y0000"
    },
    {
    "idCarrera": "-23a20229:123336a8d3c:-7de0",
    "nombre": "Ingeniería en Automática (CPE)",
    "tipo_curso": "03",
    "facultad": "R0000"
    },
    {
     "idCarrera": "010600",
    "nombre": "Ingeniería en Informatica (CD)",
    "tipo_curso": "01",
    "facultad": "R0000"
    },
    {
    "idCarrera": "010300",
    "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
    "tipo_curso": "01",
    "facultad": "X0000"
    }
    ]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_carnet_para_Persona(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dumm_carnet_x_lote(area):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "5",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"},
         {"identification": "02032466728", "area": "Facultad de Ingenieria Informatica",
          "personType": "Student", "studentYear": "5",
          "name": "Jose", "surname": "de Jesus", "lastname": "Perez"}
         ]

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm", DummyBuscarPersonaFormLotesOn)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_x_lote", dumm_carnet_x_lote)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 200  # Debe devolver una respuesta exitosa

@pytest.mark.asyncio
async def test_home_post_success_carnet_x_lotes_on_not_found(monkeypatch):
    # Token de acceso falso
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "Ingeniería Mecánica (CPE)",
    "tipo_curso": "03",
    "facultad": "X0000"
    },
    {
    "idCarrera": "0000Y1",
    "nombre": "Ingeniería Química (CPE)",
    "tipo_curso": "03",
    "facultad": "Y0000"
    },
     {
    "idCarrera": "010901",
    "nombre": "Ingeniería Química (CED)",
    "tipo_curso": "05"
    },
    {
    "idCarrera": "010900",
    "nombre": "Ingeniería Química (CD)",
    "tipo_curso": "01",
    "facultad": "Y0000"
    },
    {
    "idCarrera": "-23a20229:123336a8d3c:-7de0",
    "nombre": "Ingeniería en Automática (CPE)",
    "tipo_curso": "03",
    "facultad": "R0000"
    },
    {
     "idCarrera": "010600",
    "nombre": "Ingeniería en Informatica (CD)",
    "tipo_curso": "01",
    "facultad": "R0000"
    },
    {
    "idCarrera": "010300",
    "nombre": "Ingeniería en Metalurgia y Materiales (CD)",
    "tipo_curso": "01",
    "facultad": "X0000"
    }
    ]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_carnet_para_Persona(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dummy_buscar_personas_por_areas_ci(area, ci):
        return [{"identification": "02032466727", "area": "Facultad de Ingenieria Informatica",
         "personType": "Student", "studentYear": "1",
         "name": "Enmanuel", "surname": "de Jesus", "lastname": "Santamaria Diaz"}]

    def dumm_carnet_x_lote(area):
        return []

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.BuscarPersonaForm", DummyBuscarPersonaFormLotesOn)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_para_Persona", dummy_carnet_para_Persona)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscar_personas_por_areas_ci",dummy_buscar_personas_por_areas_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_x_lote", dumm_carnet_x_lote)

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 200  # Debe devolver una respuesta exitosa
    assert "No se encontraron estudiantes en el area especificada" in response.text
