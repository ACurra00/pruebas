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

@pytest.mark.asyncio
async def test_buscar_matriculados_get_success(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken123"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
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
    "nombre": "Ingeniería en Automática (CD)",
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


            # Parches con monkeypatch
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 200  # Verifica que devuelve correctamente el HTML

@pytest.mark.asyncio
async def test_buscar_matriculados_get_fail_connection(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken123"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
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
    "nombre": "Ingeniería en Automática (CD)",
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

            # Parches con monkeypatch
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.listaAreas", dummy_lista_areas)
    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/matriculados/crear")

    # Verificaciones
    assert response.status_code == 503  # Verifica que devuelve correctamente el HTML
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."