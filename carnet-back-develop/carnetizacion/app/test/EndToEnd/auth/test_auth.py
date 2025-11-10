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
from fastapi import status,HTTPException
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


class DummyLoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username = "ceejesus"
        self.password = "XLR8"

    async def load_data(self):
        form = await self.request.form()
        self.username = "ceejesus"
        if self.username is not None:
            self.username = "ceejesus"
        self.password = "XLR8"
        if self.password is not None:
            self.password = "XLR8"
        ##print(" user name "+self.username+ " contraseña: "+self.password)

    async def is_valid(self):
        if not self.username:
            self.errors.append("Usuario es requerido")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Una contraseña valida es requerida")
        if not self.errors:
            return True
        return False

@pytest.mark.asyncio
async def test_autenticar_sucess(monkeypatch):
    # Usuario simulado autenticado
    usuario_autenticado = Usuario(id=1, nombre_usuario="ceejesus", is_activo=True, rol_usuario="Administrador")

    def dummy_get_user(nombre_usuario, db):
        return usuario_autenticado

    def dummy_login_for_access_token(response, form, db):
        return {"access_token": "BearerToken1981421525", "token_type": "bearer"}

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("webapp.auth.router_login.LoginForm", DummyLoginForm)
    monkeypatch.setattr("webapp.auth.router_login.get_user", dummy_get_user)
    monkeypatch.setattr("webapp.auth.router_login.login_for_access_token", dummy_login_for_access_token)
    monkeypatch.setattr("webapp.auth.router_login.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login")

    assert response.status_code == 302


@pytest.mark.asyncio
async def test_autenticar_fail_invalid_user_or_password(monkeypatch):

    def dummy_get_user(nombre_usuario, db):
        return None

    def dummy_login_for_access_token(response, form, db):
        return {"access_token": "BearerToken1981421525", "token_type": "bearer"}

    monkeypatch.setattr("webapp.auth.router_login.LoginForm", DummyLoginForm)
    monkeypatch.setattr("webapp.auth.router_login.get_user", dummy_get_user)
    monkeypatch.setattr("webapp.auth.router_login.login_for_access_token", dummy_login_for_access_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login")

    assert response.status_code == 200
    assert "Incorrecto Usuario o Contraseña" in response.text

@pytest.mark.asyncio
async def test_autenticar_fail_invalid_user_does_not_exist_ldap(monkeypatch):
    # Usuario simulado autenticado
    usuario_autenticado = Usuario(id=1, nombre_usuario="ceejesus", is_activo=True, rol_usuario="Administrador")

    def dummy_get_user(nombre_usuario, db):
        return usuario_autenticado

    def dummy_login_for_access_token(response, form, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    monkeypatch.setattr("webapp.auth.router_login.LoginForm", DummyLoginForm)
    monkeypatch.setattr("webapp.auth.router_login.get_user", dummy_get_user)
    monkeypatch.setattr("webapp.auth.router_login.login_for_access_token", dummy_login_for_access_token)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login")

    assert response.status_code == 200
    assert "Incorrecto Usuario o Contraseña" in response.text