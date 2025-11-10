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
async def test_buscar_persona_get_success(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken123"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [{"distinguishedName": "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu",
                 "name": "Facultad de Ingenieria Informatica"}]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_lista_areas(areas):
       return ('API Test Read,Cristobal Revistas,Kasim Derron Ronnie Mckie,LOGS LOGS,Querys LDAP,Sistema-CETA,TEST QR,Vivian Breatriz Elena Parnas,credenciales,Area Central,Centro de Aislamiento, Computers, Facultad de Arquitectura, Facultad de Ingenieria Civil, Facultad de Ingenieria Electrica, Facultad de Ingenieria Industrial, Facultad de Ingenieria Informatica,'
         ' Facultad de Ingenieria Mecanica, Facultad de Ingenieria Quimica, Facultad de Ingenieria en Automatica y Biomedica, Facultad de Ingenieria en Tele'
         'comunicaciones y Electronica, Instituto Ciencias Basicas, Read_QR_Proyect, Temporal, Users, VPN_ACCESS, DG de ICI Area Central, ', 27)

            # Parches con monkeypatch
    monkeypatch.setattr("webapp.home.router_home.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.home.router_home.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.home.router_home.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.home.router_home.listaAreas", dummy_lista_areas)
    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/")

    # Verificaciones
    assert response.status_code == 200  # Verifica que devuelve correctamente el HTML

@pytest.mark.asyncio
async def test_buscar_persona_get_fail_connection(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken123"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_buscarAreas():
        return [{"distinguishedName": "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu",
                 "name": "Facultad de Ingenieria Informatica"}]

    def dummy_buscarAreas_por_name(areas, area):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_lista_areas(areas):
       return ('API Test Read,Cristobal Revistas,Kasim Derron Ronnie Mckie,LOGS LOGS,Querys LDAP,Sistema-CETA,TEST QR,Vivian Breatriz Elena Parnas,credenciales,Area Central,Centro de Aislamiento, Computers, Facultad de Arquitectura, Facultad de Ingenieria Civil, Facultad de Ingenieria Electrica, Facultad de Ingenieria Industrial, Facultad de Ingenieria Informatica,'
         ' Facultad de Ingenieria Mecanica, Facultad de Ingenieria Quimica, Facultad de Ingenieria en Automatica y Biomedica, Facultad de Ingenieria en Tele'
         'comunicaciones y Electronica, Instituto Ciencias Basicas, Read_QR_Proyect, Temporal, Users, VPN_ACCESS, DG de ICI Area Central, ', 27)

            # Parches con monkeypatch
    monkeypatch.setattr("webapp.home.router_home.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.home.router_home.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.home.router_home.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.home.router_home.listaAreas", dummy_lista_areas)
    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/")

    # Verificaciones
    assert response.status_code == 503  # Verifica que devuelve correctamente el HTML
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."