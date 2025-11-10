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

    def dummy_lista_usuarios(db):
        return ["Raul", "Ernesto"]

    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.lista_usuarios",dummy_lista_usuarios)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin")

    assert response.status_code == 200
    assert "Usuarios" in response.text

@pytest.mark.asyncio
async def test_mostrar_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_usuarios(db):
        return ["Raul", "Ernesto"]

    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.lista_usuarios",dummy_lista_usuarios)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_mostrar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_lista_usuarios(db):
        return ["Raul", "Ernesto"]

    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.lista_usuarios",dummy_lista_usuarios)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin")

    assert response.status_code == 302
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_mostrar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_lista_usuarios(db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_usuarios.lista_usuarios",dummy_lista_usuarios)


    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

'''GET de crear usaurios'''
@pytest.mark.asyncio
async def test_mostrar_form_crear_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin/form_usuario")

    assert response.status_code == 200
    assert "Usuario" in response.text

@pytest.mark.asyncio
async def test_mostrar_form_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin/form_usuario")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_mostrar_form_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin/form_usuario")

    assert response.status_code == 302
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_mostrar_form_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/usuario_admin/form_usuario")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

'''POST de crear usaurios'''
class DummyCrearUsuarioForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.error_nombre_usuario = ""
        self.nombre_usuario = "ceejesus"
        self.rol_usuario = "Carnetizador"

    async def load_data(self):
        form = await self.request.form()
        self.nombre_usuario = "ceejesus"
        if self.nombre_usuario is not None:
            self.nombre_usuario = "ceejesus"
        self.rol_usuario = "Carnetizador"
        if self.rol_usuario is not None:
            self.rol_usuario = "Carnetizador"


    async def is_valid(self):
        if not self.nombre_usuario or self.nombre_usuario == "":
            self.error_nombre_usuario = "*Este campo es obligatorio"
            return False
        elif not self.rol_usuario or self.rol_usuario == "Seleccione":
            return False
        else:
            return True

@pytest.mark.asyncio
async def test_crear_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    listUsers = [Usuario(id=1, nombre_usuario="ceediazp", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_usuarios(db):
        return listUsers

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)
        return listUsers[2]

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        return [{"user": "ceejesus"}]

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 302
    assert listUsers[2].nombre_usuario == "ceejesus"

@pytest.mark.asyncio
async def test_crear_fail_no_exist_ldap(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    listUsers = [Usuario(id=1, nombre_usuario="ceediazp", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_usuarios(db):
        return listUsers

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        return None

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 200
    assert "El usuario no existe en el ldap" in response.text

@pytest.mark.asyncio
async def test_crear_fail_exist(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    listUsers = [Usuario(id=1, nombre_usuario="ceejesus", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_usuarios(db):
        return listUsers

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        return [{"user": "ceejesus"}]

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 200
    assert "El usuario ya existe" in response.text

@pytest.mark.asyncio
async def test_crear_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    listUsers = [Usuario(id=1, nombre_usuario="ceediazp", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_lista_usuarios(db):
        return listUsers

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        return [{"user": "ceejesus"}]

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_crear_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    listUsers = [Usuario(id=1, nombre_usuario="ceediazp", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token


    def dummy_lista_usuarios(db):
        return listUsers

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        return [{"user": "ceejesus"}]

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 401
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_crear_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    listUsers = [Usuario(id=1, nombre_usuario="ceediazp", rol_usuario="Carnetizador"),
                Usuario(id=2, nombre_usuario="ceediazr", rol_usuario="Administrador")]

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")


    def dummy_lista_usuarios(db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_create_new_user(user, db):
        usuario_objeto = Usuario(**user.dict())
        listUsers.append(usuario_objeto)

    def dummy_buscarTrabajdor_and_Estudiante(ci):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.lista_usuarios",dummy_lista_usuarios)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.create_new_user", dummy_create_new_user)
    monkeypatch.setattr("webapp.admin.usuarios.router_form_usuarios.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajdor_and_Estudiante)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post("/usuario_admin/form_usuario")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

'''GET de editar usuarios'''
@pytest.mark.asyncio
async def test_mostrar_form_editar_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_retreive_usuario(id, db):
        return "ok"

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario",dummy_retreive_usuario)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 200
    assert "Usuario" in response.text

@pytest.mark.asyncio
async def test_mostrar_form_editar_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_retreive_usuario(id, db):
        return "ok"

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario",dummy_retreive_usuario)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_mostrar_form_editar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_retreive_usuario(id, db):
        return "ok"

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario",dummy_retreive_usuario)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_mostrar_form_editar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_retreive_usuario(id, db):
        return "ok"

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario",dummy_retreive_usuario)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."

'''POST de editar usuarios'''
@pytest.mark.asyncio
async def test_editar_sucess(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    usuario_actual = Usuario(id=1, nombre_usuario="ceejesus", rol_usuario="Administrador")
    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_update_usuario_by_id(id, usuario, db):
        usuario_objeto = Usuario(**usuario.dict())
        usuario_actual.rol_usuario = usuario_objeto.rol_usuario

    def dummy_retreive_usuario(id, db):
        return usuario_actual

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.update_usuario_by_id", dummy_update_usuario_by_id)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario", dummy_retreive_usuario)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.create_new_registro", dummy_create_new_registro)
    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/usuario_admin/form_usuario/{id}")


    assert response.status_code == 302
    assert usuario_actual.rol_usuario == "Carnetizador"

@pytest.mark.asyncio
async def test_editar_fail_not_admin(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    usuario_actual = Usuario(id=1, nombre_usuario="ceejesus", rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Simula autenticación exitosa

    def dummy_update_usuario_by_id(id, usuario, db):
        usuario_objeto = Usuario(**usuario.dict())
        usuario_actual.rol_usuario = usuario_objeto.rol_usuario

    def dummy_retreive_usuario(id, db):
        return usuario_actual

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.update_usuario_by_id", dummy_update_usuario_by_id)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario", dummy_retreive_usuario)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/usuario_admin/form_usuario/{id}")


    assert response.status_code == 302
    assert response.headers["location"] == "/login"

@pytest.mark.asyncio
async def test_editar_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    usuario_actual = Usuario(id=1, nombre_usuario="ceejesus", rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_update_usuario_by_id(id, usuario, db):
        usuario_objeto = Usuario(**usuario.dict())
        usuario_actual.rol_usuario = usuario_objeto.rol_usuario

    def dummy_retreive_usuario(id, db):
        return usuario_actual

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.update_usuario_by_id", dummy_update_usuario_by_id)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario", dummy_retreive_usuario)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 401
    assert response.headers["location"] == "login"

@pytest.mark.asyncio
async def test_editar_fail_connection(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    usuario_actual = Usuario(id=1, nombre_usuario="ceejesus", rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_update_usuario_by_id(id, usuario, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_retreive_usuario(id, db):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.CrearUsuarioForm", DummyCrearUsuarioForm)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.update_usuario_by_id", dummy_update_usuario_by_id)
    monkeypatch.setattr("webapp.admin.usuarios.router_edit_usuario.retreive_usuario", dummy_retreive_usuario)

    id = 1
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.post(f"/usuario_admin/form_usuario/{id}")

    assert response.status_code == 503
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."
