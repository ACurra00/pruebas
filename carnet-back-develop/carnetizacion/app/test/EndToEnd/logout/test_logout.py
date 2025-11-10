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

@pytest.mark.asyncio
async def test_logout_success(monkeypatch):
    fake_token = "Bearer testtoken123"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_update_state_usuario_by_id_logout(id, db):
        return "ok"

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    monkeypatch.setattr("api.endpoints.router_login.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("api.endpoints.router_login.update_state_usuario_by_id_logout",dummy_update_state_usuario_by_id_logout)
    monkeypatch.setattr("api.endpoints.router_login.create_new_registro", dummy_create_new_registro)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/cerrarsesion")

    assert response.status_code == 302

@pytest.mark.asyncio
async def test_logout_fail_invalid_token(monkeypatch):
    fake_token = "Bearer testtoken124"

    # Usuario simulado autenticado
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Administrador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_update_state_usuario_by_id_logout(id, db):
        return "ok"

    monkeypatch.setattr("api.endpoints.router_login.get_current_user_from_token",dummy_get_current_user_from_token)
    monkeypatch.setattr("api.endpoints.router_login.update_state_usuario_by_id_logout",dummy_update_state_usuario_by_id_logout)

    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get("/cerrarsesion")

    assert response.status_code == 302