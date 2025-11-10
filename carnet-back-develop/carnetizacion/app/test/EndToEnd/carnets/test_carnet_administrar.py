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

from db.models.registro import Registro


class DummySession:
    def close(self):
        pass

def override_get_db() -> Session:
    return DummySession()

# Sobrescribe las dependencias get_db y get_db_roles
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_roles] = override_get_db

DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

class FakeQuerySet:
    def __init__(self, data):
        self.data = data

    def count(self):
        return len(self.data)

    def __iter__(self):  # Para poder iterar sobre el resultado
        return iter(self.data)

    def all(self):  # Simula .all() de SQLAlchemy
        return self.data

@pytest.mark.asyncio
async def test_mostrar_sucess(monkeypatch):
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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar")

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_buscar_para_cambiar_sucess(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        )
    ])

    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Seminterno"))]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_carnet_activo_x_ci(db, carnet_ci):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_ci(db, ci):
        return DUMMY_PERSON_RESPONSE

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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_ci", dummy_lista_carnet_activo_x_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_ci",dummy_list_personas_por_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro1": "02032466727"})

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_buscar_para_cambiar_fail_not_found(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([])
    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_carnet_activo_x_ci(db, carnet_ci):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_ci(db, ci):
        return []

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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_ci", dummy_lista_carnet_activo_x_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_ci",dummy_list_personas_por_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro1": "02032466727"})

    assert response.status_code == 200
    assert "No hay resultados para los campos especificados" in response.text

@pytest.mark.asyncio
async def test_administrar_fail_invalid_token(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        )
    ])

    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Seminterno"))]

    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_lista_carnet_activo_x_ci(db, carnet_ci):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_ci(db, ci):
        return DUMMY_PERSON_RESPONSE

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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_ci", dummy_lista_carnet_activo_x_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_ci",dummy_list_personas_por_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro1": "02032466727"})

    assert response.status_code == 302
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_administrar_fail_connection(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        )
    ])

    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Seminterno"))]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_lista_carnet_activo_x_ci(db, carnet_ci):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_ci(db, ci):
        return DUMMY_PERSON_RESPONSE

    def dummy_buscarAreas():
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_ci", dummy_lista_carnet_activo_x_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_ci",dummy_list_personas_por_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro1": "02032466727"})

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_buscar_por_nombre_para_cambiar_sucess(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        )
    ])

    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="c", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Seminterno"))]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_carnet_activo_x_nombre(db, nombre):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_nombre(db, nombre):
        return DUMMY_PERSON_RESPONSE

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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_nombre", dummy_lista_carnet_activo_x_nombre)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_nombre",dummy_list_personas_por_nombre)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro3": "Enmanuel Rodriguez"})

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cambiar_uno_sucess(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = [CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))]


    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Seminterno"))]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_cambiar_estado(db, estado, ci_carnet):
        for carnet in DUMMY_CARNET_RESPONSE:
            if carnet.person_ci == ci_carnet:
                carnet.estado = estado
                return carnet
        raise Exception("Carnet no encontrado")

    def dummy_lista_carnet_activo_x_ci(db, carnet_ci):
        return DUMMY_CARNET_RESPONSE

    def dummy_list_personas_por_ci(db, ci):
        return DUMMY_PERSON_RESPONSE

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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario cambió el estado de un carnet", tipo="Cambiar estado")

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_activo_x_ci", dummy_lista_carnet_activo_x_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_ci",dummy_list_personas_por_ci)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.cambiar_estado", dummy_cambiar_estado)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"estado": "Entregado",
                                                                    "carnet_id": "02032466727"})

    assert response.status_code == 200
    assert DUMMY_CARNET_RESPONSE[0].estado == "Entregado"

@pytest.mark.asyncio
async def test_buscar_lote_para_cambiar_sucess(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE = FakeQuerySet([
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        ),
        DummyRow(
            CarnetActivo(id=1, person_ci="02032466728", folio=2, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
        )
    ])

    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Docente")),
        DummyRow2(
            Person(ci="02032466728", nombre="Jesus Rodriguez", is_activa=True
                   , area="DG de ICI Area Central", rol="Docente"))
    ]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista__hechos_tipo(db, tipo, area):
        return DUMMY_CARNET_RESPONSE

    def dummy_lista_personas_por_area_tipo(db, area, tipo):
        return DUMMY_PERSON_RESPONSE

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "DG de ICI Area Central",
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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_hechos_tipo", dummy_lista__hechos_tipo)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_area_tipo",dummy_lista_personas_por_area_tipo)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"filtro4": "DG de ICI Area Central",
                                                                    "filtro5": "change_Docente"})

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cambiar_lotes_sucess(monkeypatch):
    DummyRow = namedtuple("DummyRow", ["CarnetActivo"])

    DUMMY_CARNET_RESPONSE =  [CarnetActivo(id=1, person_ci="02032466727", folio=1, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))
    , CarnetActivo(id=1, person_ci="02032466728", folio=2, tipo_motivo_id=1,
                         comprobante_motivo="A", estado="Hecho", fecha=datetime(2025, 2, 17))]



    DummyRow2 = namedtuple("DummyRow2", ["Person"])

    DUMMY_PERSON_RESPONSE = [DummyRow2(
        Person(ci="02032466727", nombre ="Enmanuel Rodriguez", is_activa = True
                    , area = "Facultad de Ingenieria Informatica", rol = "Docente")),
        DummyRow2(
            Person(ci="02032466728", nombre="Jesus Rodriguez", is_activa=True
                   , area="DG de ICI Area Central", rol="Docente"))
    ]

    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista__hechos_tipo(db, tipo, area, estado):
        return DUMMY_CARNET_RESPONSE

    def dummy_lista_personas_por_area_tipo(db, area, tipo):
        return DUMMY_PERSON_RESPONSE

    def dummy_buscarAreas():
        return [

     {
    "idCarrera": "010401",
    "nombre": "DG de ICI Area Central",
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

    def dummy_lista_areas(areas):
       return ('Arquitectura (CD),Curso de Preparación - Ing. Civil (CD),Curso de Preparación - Ing. Hidráulica (CD),Ingeniería Biomédica (CD),Ingeniería Civil (CD),Ingeniería Civil (CPE),Ingeniería Eléctrica (CD),Ingeniería Eléctrica (CPE),Ingeniería Geofísica (CD),'
               'Ingeniería Hidráulica (CPE),Ingeniería Hidráulica (CD),Ingeniería Industrial (CCE),Ingeniería Industrial (CD),Ingeniería Industrial (CPE),Ingeniería Industrial (CCE),Ingeniería Industrial (CCE)'
               ',Ingeniería Industrial (CPE),Ingeniería Informática (CCE),Ingeniería Informática (CPE),Ingeniería Informática (CPE),Ingeniería Informática (CCE),'
               'Ingeniería Informática (CED),Ingeniería Informática (CD),Ingeniería Mecánica (CD),Ingeniería Mecánica (CPE),Ingeniería Química (CPE),Ingeniería Química (CED),Ingeniería Química (CD),Ingeniería en Automática (CPE),Ingeniería en Automática (CD),Ingeniería en Metalurgia y Materiales (CD),Ingeniería en Metalurgia y Materiales (CPE),'
               'Ingeniería en Telecomunicaciones y Electrónica (CPE),Ingeniería en Telecomunicaciones y Electrónica (CD),Organización de Empresas (CD),Técnico Superior en Agua y Saneamiento (CCPE),Técnico Superior en Inversiones Constructivas (CCPE),Técnico Superior en Logística (CCPE),Técnico Superior en Logística (CCD)'
               ',Técnico Superior en Mantenimiento para el Turismo (CCD),Técnico Superior en Metrología (CCD),Técnico Superior en Transporte Automotor (CCD),', 42)

    def dummy_cambiar_estado_por_cantidad(db, estado, area, rol):
        for carnet in DUMMY_CARNET_RESPONSE:
                carnet.estado = estado
        return "ok"
    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario cambió el estado de un carnet", tipo="Cambiar estado")

    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.lista_carnet_tipo", dummy_lista__hechos_tipo)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.list_personas_por_area_tipo",dummy_lista_personas_por_area_tipo)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.buscarAreas",dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.listaAreas", dummy_lista_areas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.cambiar_estado_por_cantidad", dummy_cambiar_estado_por_cantidad)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_carnet_administrar.create_new_registro",dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/carnets/administrar", params={"estado": "Entregado",
                                                                    "area": "DG de ICI Area Central",
                                                                    "rol": "Docente"})

    assert response.status_code == 200
    for carnet in DUMMY_CARNET_RESPONSE:
        assert carnet.estado == "Entregado"


