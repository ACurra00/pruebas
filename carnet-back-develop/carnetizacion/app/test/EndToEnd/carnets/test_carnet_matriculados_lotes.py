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

from db.models.registro import Registro


class DummySession:
    def close(self):
        pass

def override_get_db() -> Session:
    return DummySession()

# Sobrescribe las dependencias get_db y get_db_roles
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_roles] = override_get_db

#Test en el caso en que se crean bien:
@pytest.mark.asyncio
async def test_crear_solicitud_carnetxlotesmatriculados_success(monkeypatch):
    # Generar un token falso manualmente
    fake_token = "Bearer testtoken123"

    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_carnet_por_lotes(area, request, db, dbroles):
        return "ok"

    def dummy_create_new_registro(db: Session, username: str, accion: str, tipo: str):
        return Registro(username="ceejesus", accion="El usuario se autenticó", tipo="Autenticarse")

    # Reemplaza la función real por la dummy.
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_por_lotes", dummy_carnet_por_lotes)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.create_new_registro", dummy_create_new_registro)

    # Valores de entrada según el caso de éxito
    area = "Facultad de Ingenieria Informatica"

    # Usa AsyncClient para simular la petición GET a la ruta
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/carnetXLotesMatriculados/{area}")

    # Verifica que la respuesta tenga status 302 (redirect)
    assert response.status_code == 302
    # Verifica que la cabecera "location" apunte a "/carnets/solicitados"
    assert response.headers.get("location") == "/carnets/solicitados"

#Test en el caso en que el token es invalido y redirecciona al login:
@pytest.mark.asyncio
async def test_crear_solicitud_carnetxlotesmatriculados_fail_invalid_token(monkeypatch):
    # Generar un token falso manualmente
    fake_token = "Bearer testtoken124"

    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_carnet_por_lotes(area, request, db, dbroles):
        return "ok"

    # Reemplaza la función real por la dummy.
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_por_lotes", dummy_carnet_por_lotes)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)

    # Valores de entrada según el caso de éxito
    area = "Facultad de Ingenieria Informatica"

    # Usa AsyncClient para simular la petición GET a la ruta
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/carnetXLotesMatriculados/{area}")

    # Verifica que la respuesta tenga status 302 (redirect)
    assert response.status_code == 302
    # Verifica que la cabecera "location" apunte a login
    assert response.headers.get("location") == "login"

#Test en el caso en que falla la conexion y se muestra mensaje:
@pytest.mark.asyncio
async def test_crear_solicitud_carnetxlotesmatriculados_fail_connection_error(monkeypatch):
    # Generar un token falso manualmente
    fake_token = "Bearer testtoken123"

    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    def dummy_get_current_user_from_token(param, db):
        return usuario_autenticado_token  # Devuelve el usuario simulado

    def dummy_carnet_por_lotes(area, request, db, dbroles):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    # Reemplaza la función real por la dummy.
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.carnet_por_lotes", dummy_carnet_por_lotes)
    monkeypatch.setattr("webapp.crear_carnet.carnets.router_crear_matriculados.get_current_user_from_token", dummy_get_current_user_from_token)

    # Valores de entrada según el caso de éxito
    area = "Facultad de Ingenieria Informatica"

    # Usa AsyncClient para simular la petición GET a la ruta
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)
        response = await client.get(f"/carnetXLotesMatriculados/{area}")

    # Verifica que la respuesta tenga status 302 (redirect)
    assert response.status_code == 503
    # Verifica que el detalle del error sea correcto
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."