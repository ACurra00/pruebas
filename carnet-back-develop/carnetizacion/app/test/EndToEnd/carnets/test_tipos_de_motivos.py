import html
import os
import zipfile
from collections import namedtuple
from datetime import datetime
from io import BytesIO
from typing import List
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
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin")

    assert response.status_code == 200
    assert "Tipos de Motivos" in response.text


@pytest.mark.asyncio
async def test_mostrar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin")

    assert response.status_code == 302
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_mostrar_vista_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin")

    assert response.status_code == 302
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto



@pytest.mark.asyncio
async def test_mostrar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_admin.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_mostrar_formulario_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin/crear-motivo")

    assert response.status_code == 200
    assert "Tipo de Motivo" in response.text

@pytest.mark.asyncio
async def test_mostrar_formulario_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin/crear-motivo")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_mostrar_formulario_crear_fail_invalid_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin/crear-motivo")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"  # Verifica que redirige al lugar correcto


@pytest.mark.asyncio
async def test_mostrar_formulario_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_list_motivos(db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/motivos_admin/crear-motivo")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

class DummyCrearMotivoForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.error_nombre_motivo = ""
        self.nombre_motivo = "Nuevo Ingreso"

    async def load_data(self):
        form = await self.request.form()
        self.nombre_motivo = "Nuevo Ingreso"

    async def is_valid(self):
        if not self.nombre_motivo or self.nombre_motivo == "":
            self.error_nombre_motivo = "*Este campo es obligatorio"
            return False
        else:
            return True

@pytest.mark.asyncio
async def test_crear_success(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return [TipoMotivo(id_motivo=1, nombre_motivo="Cambio de area"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]

    def dummy_create_tipo_motivo(tipo_motivo, db):
        return "ok"

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.CrearMotivoForm", DummyCrearMotivoForm)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.create_tipo_motivo", dummy_create_tipo_motivo)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/motivos_admin/crear-motivo")

    assert response.status_code == 302

@pytest.mark.asyncio
async def test_crear_fail_existing(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return [TipoMotivo(id_motivo=1, nombre_motivo="Nuevo Ingreso"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]

    def dummy_create_tipo_motivo(tipo_motivo, db):
        return "ok"


    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.CrearMotivoForm", DummyCrearMotivoForm)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.create_tipo_motivo", dummy_create_tipo_motivo)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/motivos_admin/crear-motivo")

    assert response.status_code == 200
    assert "El motivo ya existe" in response.text

@pytest.mark.asyncio
async def test_crear_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return [TipoMotivo(id_motivo=1, nombre_motivo="Nuevo Ingreso"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]

    def dummy_create_tipo_motivo(tipo_motivo, db):
        return "ok"
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.CrearMotivoForm", DummyCrearMotivoForm)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.create_tipo_motivo", dummy_create_tipo_motivo)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/motivos_admin/crear-motivo")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"  # Verifica que redirige al lugar correcto

@pytest.mark.asyncio
async def test_crear_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return [TipoMotivo(id_motivo=1, nombre_motivo="Nuevo Ingreso"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]

    def dummy_create_tipo_motivo(tipo_motivo, db):
        return "ok"
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.CrearMotivoForm", DummyCrearMotivoForm)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.router_motivos_crear.create_tipo_motivo", dummy_create_tipo_motivo)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/motivos_admin/crear-motivo")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_mostrar_formulario_edit_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    def dummy_retreive_motivo(id, db):
        return TipoMotivo(id_motivo = 1, nombre_motivo = "Traslado")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 200
    assert "Tipo de Motivo" in response.text

@pytest.mark.asyncio
async def test_mostrar_formulario_edit_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    def dummy_retreive_motivo(id, db):
        return TipoMotivo(id_motivo = 1, nombre_motivo = "Traslado")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

@pytest.mark.asyncio
async def test_mostrar_formulario_edit_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    def dummy_retreive_motivo(id, db):
        return TipoMotivo(id_motivo = 1, nombre_motivo = "Traslado")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_mostrar_formulario_edit_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de area"]

    def dummy_retreive_motivo(id, db):
        return TipoMotivo(id_motivo = 1, nombre_motivo = "Traslado")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 302
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_edit_fail_success(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")
    motivos = [TipoMotivo(id_motivo=1, nombre_motivo="Traslado"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return motivos

    def dummy_retreive_motivo(id, db):
        return motivos[0]

    def dummy_update_motivo_by_id(id, tipo_motivo, db):
       motivos[0].nombre_motivo = tipo_motivo.nombre_motivo

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.update_motivo_by_id",dummy_update_motivo_by_id)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.CrearMotivoForm", DummyCrearMotivoForm)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.create_new_registro", dummy_create_new_registro)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 302
    assert  motivos[0].nombre_motivo == "Nuevo Ingreso"


@pytest.mark.asyncio
async def test_edit_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")
    motivos = [TipoMotivo(id_motivo=1, nombre_motivo="Traslado"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return motivos

    def dummy_retreive_motivo(id, db):
        return motivos[0]

    def dummy_update_motivo_by_id(id, tipo_motivo, db):
       motivos[0].nombre_motivo = tipo_motivo.nombre_motivo

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.update_motivo_by_id",dummy_update_motivo_by_id)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.CrearMotivoForm", DummyCrearMotivoForm)
    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 302
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_edit_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")
    motivos = [TipoMotivo(id_motivo=1, nombre_motivo="Traslado"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return motivos

    def dummy_retreive_motivo(id, db):
        return motivos[0]

    def dummy_update_motivo_by_id(id, tipo_motivo, db):
       motivos[0].nombre_motivo = tipo_motivo.nombre_motivo

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.update_motivo_by_id",dummy_update_motivo_by_id)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.CrearMotivoForm", DummyCrearMotivoForm)
    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 401

class DummyCrearMotivoForm2:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.error_nombre_motivo = ""
        self.nombre_motivo = "Traslado"

    async def load_data(self):
        form = await self.request.form()
        self.nombre_motivo = "Traslado"

    async def is_valid(self):
        if not self.nombre_motivo or self.nombre_motivo == "":
            self.error_nombre_motivo = "*Este campo es obligatorio"
            return False
        else:
            return True

@pytest.mark.asyncio
async def test_edit_fail_exist(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")
    motivos = [TipoMotivo(id_motivo=1, nombre_motivo="Traslado"), TipoMotivo(id_motivo=2, nombre_motivo="Cambio de rol")]
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_list_motivos(db):
        return motivos

    def dummy_retreive_motivo(id, db):
        return motivos[0]

    def dummy_update_motivo_by_id(id, tipo_motivo, db):
       motivos[0].nombre_motivo = tipo_motivo.nombre_motivo

    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.list_motivos",dummy_list_motivos)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.retreive_motivo", dummy_retreive_motivo)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.update_motivo_by_id",dummy_update_motivo_by_id)
    monkeypatch.setattr("webapp.admin.tipo_de_motivos.editar_tipo_motivo.router_edit_tipo_motivo.CrearMotivoForm", DummyCrearMotivoForm2)
    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/motivos_admin/editar-motivo/{id}")

    assert response.status_code == 200
    assert "El motivo ya existe" in response.text



