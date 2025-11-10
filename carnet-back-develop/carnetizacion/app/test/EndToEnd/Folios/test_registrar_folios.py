import html
import os
import zipfile
from collections import namedtuple
from datetime import datetime
from io import BytesIO
from typing import List, Optional
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
from fastapi import Request
from db.models.tipo_motivo import TipoMotivo
from db.models.folio_cont import Folio_Cont

from db.models.registro import Registro


class DummySession:
    def close(self):
        pass

def override_get_db() -> Session:
    return DummySession()

# Sobrescribe las dependencias get_db y get_db_roles
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_roles] = override_get_db

@pytest.mark.asyncio
async def test_mostrar_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscar_folio_por_nombre(folio, db):
        return Folio_Cont(id = 1,nombre_folio = "Seminterno", numero_1 = "1000",
           numero_2 = "2000", numero_3 = "3000", numero_4 = "4000", numero_5 = "1000", cantidad_hojas = "1300")

    monkeypatch.setattr("webapp.folio.router_folio.buscar_folio_por_nombre", dummy_buscar_folio_por_nombre)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/registrar_folio")

    assert response.status_code == 200
    assert "Seminterno" in response.text

@pytest.mark.asyncio
async def test_mostrar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscar_folio_por_nombre(folio, db):
        return Folio_Cont(id = 1,nombre_folio = "Seminterno", numero_1 = "1000",
           numero_2 = "2000", numero_3 = "3000", numero_4 = "4000", numero_5 = "1000", cantidad_hojas = "1300")

    monkeypatch.setattr("webapp.folio.router_folio.buscar_folio_por_nombre", dummy_buscar_folio_por_nombre)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/registrar_folio")

    assert response.status_code == 302
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_mostrar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_buscar_folio_por_nombre(folio, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.folio.router_folio.buscar_folio_por_nombre", dummy_buscar_folio_por_nombre)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/registrar_folio")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

''''POST'''


class DummyFolioForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.cont_folio_numero_1 = 1001
        self.cont_folio_numero_2 = 2001
        self.cont_folio_numero_3 = 3001
        self.cont_folio_numero_4 = 4001
        self.cont_folio_numero_5 = 5001
        self.cont_cantidad_hojas = 1200

        self.errorfolio_numero_1: Optional[str] = ""
        self.errorfolio_numero_2: Optional[str] = ""
        self.errorfolio_numero_3: Optional[str] = ""
        self.errorfolio_numero_4: Optional[str] = ""
        self.errorfolio_numero_5: Optional[str] = ""
        self.errorCantidad_hojas: Optional[str] = ""

    async def load_data(self):
        form = await self.request.form()

        self.cont_folio_numero_1 = 1001
        if self.cont_folio_numero_1 is not None:
            self.cont_folio_numero_1 = 1001
        self.cont_folio_numero_2 = 2001
        if self.cont_folio_numero_2 is not None:
            self.cont_folio_numero_2 = 2001
        self.cont_folio_numero_3 = 3001
        if self.cont_folio_numero_3 is not None:
            self.cont_folio_numero_3 = 3001
        self.cont_folio_numero_4 = 4001
        if self.cont_folio_numero_4 is not None:
            self.cont_folio_numero_4 = 4001
        self.cont_folio_numero_5 = 5001
        if self.cont_folio_numero_5 is not None:
            self.cont_folio_numero_5 = 5001
        self.cont_cantidad_hojas = 1200
        if self.cont_cantidad_hojas is not None:
            self.cont_cantidad_hojas = 1200

    async def is_valid(self):
        error = True
        if not self.cont_folio_numero_1:
            self.errorfolio_numero_1 = "Folio numero 1 es requerido"
            error = False
        if self.cont_folio_numero_1 < 0:
            self.errorfolio_numero_1 = "El folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_2:
            self.errorfolio_numero_2 = "Folio numero 2 es requerido"
            error = False
        if self.cont_folio_numero_2 < 0:
            self.errorfolio_numero_2 = "El Folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_3:
            self.errorfolio_numero_3 = "Folio numero 3 es requerido"
            error = False
        if self.cont_folio_numero_3 < 0:
            self.errorfolio_numero_3 = "El folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_4:
            self.errorfolio_numero_4 = "Folio numero 4 es requerido"
            error = False
        if self.cont_folio_numero_4 < 0:
            self.errorfolio_numero_4 = "El folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_5:
            self.errorfolio_numero_5 = "Folio numero 5 es requerido"
            error = False
        if self.cont_folio_numero_5 < 0:
            self.errorfolio_numero_5 = "El folio debe ser mayor que 0"
            error = False

        if self.cont_cantidad_hojas > 0:
            self.errorCantidad_hojas = "La Cantidad de Hojas debe ser mayor que 0"
            error = False

        if error:
            return True

        return False

@pytest.mark.asyncio
async def test_registrar_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    folio_actual = Folio_Cont(id = 1,nombre_folio = "Seminterno", numero_1 = "1000",
           numero_2 = "2000", numero_3 = "3000", numero_4 = "4000", numero_5 = "1000", cantidad_hojas = "1000")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_update_folio_by_name(folio, n1, n2, n3, n4, n5, h, db):
        folio_actual.numero_1 = n1
        folio_actual.numero_2 = n2
        folio_actual.numero_3 = n3
        folio_actual.numero_4 = n4
        folio_actual.numero_5 = n5
        folio_actual.cantidad_hojas = h
        return "ok"

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.folio.router_folio.FolioForm", DummyFolioForm)
    monkeypatch.setattr("webapp.folio.router_folio.update_folio_by_name", dummy_update_folio_by_name)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.folio.router_folio.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/registrar_folio")

    assert response.status_code == 302
    assert folio_actual.numero_1 == "1001"
    assert folio_actual.numero_2 == "2001"
    assert folio_actual.numero_3 == "3001"
    assert folio_actual.numero_4 == "4001"
    assert folio_actual.numero_5 == "5001"
    assert folio_actual.cantidad_hojas == 1200

@pytest.mark.asyncio
async def test_registrar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    folio_actual = Folio_Cont(id = 1,nombre_folio = "Seminterno", numero_1 = "1000",
           numero_2 = "2000", numero_3 = "3000", numero_4 = "4000", numero_5 = "1000", cantidad_hojas = "1000")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_update_folio_by_name(folio, n1, n2, n3, n4, n5, h, db):
        folio_actual.numero_1 = n1
        folio_actual.numero_2 = n2
        folio_actual.numero_3 = n3
        folio_actual.numero_4 = n4
        folio_actual.numero_5 = n5
        folio_actual.cantidad_hojas = h
        return "ok"


    monkeypatch.setattr("webapp.folio.router_folio.FolioForm", DummyFolioForm)
    monkeypatch.setattr("webapp.folio.router_folio.update_folio_by_name", dummy_update_folio_by_name)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/registrar_folio")

    assert response.status_code == 302
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_registrar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    folio_actual = Folio_Cont(id = 1,nombre_folio = "Seminterno", numero_1 = "1000",
           numero_2 = "2000", numero_3 = "3000", numero_4 = "4000", numero_5 = "1000", cantidad_hojas = "1000")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_update_folio_by_name(folio, n1, n2, n3, n4, n5, h, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.folio.router_folio.FolioForm", DummyFolioForm)
    monkeypatch.setattr("webapp.folio.router_folio.update_folio_by_name", dummy_update_folio_by_name)
    monkeypatch.setattr("webapp.folio.router_folio.get_current_user_from_token", dummy_get_current_user_from_token)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/registrar_folio")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."



