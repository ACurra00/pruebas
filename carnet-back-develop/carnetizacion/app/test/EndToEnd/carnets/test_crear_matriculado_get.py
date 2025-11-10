import json
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

#Muestra bien la vista:
@pytest.mark.asyncio
async def test_crear_carnet_matriculados_get_success(monkeypatch):
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

    def dummy_buscarTrabajador_and_Estudiante(ci, areatemp):
        return [{"identification": ci, "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5", "name": "Juan", "surname": "Pérez", "lastname": "Gómez"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que la persona no tiene un carnet previo

    def dummy_buscar_trabajador_con_cargo(ci, dbroles):
        return False

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de Area"]

    def dummy_buscar_Tipo_Estudiante_carnet(ci):
        return "Seminterno"  # Simula que el estudiante tiene este tipo de carnet

    def dummy_buscar_buscar_personas_por_areas_ci(area: str, ci: str):
        # Simulación de respuesta esperada
        dummy_response = [
            {
                "identification": ci,
                "firstName": "Juan",
                "middleName": "Carlos",
                "lastName": "Pérez",
                "idCareer": area,
                "idCourseType": "Diurno",
                "idSex": "M",
                "idEntrySource": "Concurso",
                "idStudentStatus": "Activo",
                "personType": "Student",
                "studentType":"Seminterno",
                "area": "Facultad de Ingenieria Informatica"
            }
        ]

        # Simula convertir la respuesta en JSON como lo haría una solicitud real
        return json.loads(json.dumps(dummy_response))
    # Parches con monkeypatch
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajador_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.list_motivos", dummy_list_motivos)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_personas_por_areas_ci", dummy_buscar_buscar_personas_por_areas_ci)

    # Parámetros simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/crearUnMatriculado/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 200  # Verifica que devuelve correctamente el HTML

#No esta logueado, token invalido, redirecciona al loguin:
@pytest.mark.asyncio
async def test_crear_carnet_matriculados_get_fail_invalid_token(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken124"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscarAreas():
        return [{"distinguishedName": "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu",
                 "name": "Facultad de Ingenieria Informatica"}]

    def dummy_buscarAreas_por_name(areas, area):
        return "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu"

    def dummy_buscarTrabajador_and_Estudiante(ci, areatemp):
        return [{"identification": ci, "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5", "name": "Juan", "surname": "Pérez", "lastname": "Gómez"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que la persona no tiene un carnet previo

    def dummy_buscar_trabajador_con_cargo(ci, dbroles):
        return False

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de Area"]

    def dummy_buscar_Tipo_Estudiante_carnet(ci):
        return "Seminterno"  # Simula que el estudiante tiene este tipo de carnet

    def dummy_buscar_buscar_personas_por_areas_ci(area: str, ci: str):
        # Simulación de respuesta esperada
        dummy_response = [
            {
                "identification": ci,
                "firstName": "Juan",
                "middleName": "Carlos",
                "lastName": "Pérez",
                "idCareer": area,
                "idCourseType": "Diurno",
                "idSex": "M",
                "idEntrySource": "Concurso",
                "idStudentStatus": "Activo",
                "personType": "Student",
                "studentType":"Seminterno",
                "area": "Facultad de Ingenieria Informatica"
            }
        ]

        # Simula convertir la respuesta en JSON como lo haría una solicitud real
        return json.loads(json.dumps(dummy_response))
    # Parches con monkeypatch
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajador_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.list_motivos", dummy_list_motivos)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_personas_por_areas_ci", dummy_buscar_buscar_personas_por_areas_ci)

    # Parámetros simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/crearUnMatriculado/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 302  # Verifica que devuelve correctamente el HTML
    assert response.headers["location"] == "login"  # Verifica que redirige al lugar correcto

#Falla la conexion:
@pytest.mark.asyncio
async def test_crear_carnet_matriculados_get_fail_connection_error(monkeypatch):
    # Token falso de autenticación
    fake_token = "Bearer testtoken123"

    # Simula un usuario autenticado con rol de Carnetizador
    usuario_autenticado_token = Usuario(id=1, nombre_usuario="usuario1", is_activo=True, rol_usuario="Carnetizador")

    # Mock de funciones necesarias para el flujo
    def dummy_get_current_user_from_token(param, db):
        if param != "testtoken123":  # Simula que solo "testtoken123" es válido
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_autenticado_token

    def dummy_buscarAreas():
        return [{"distinguishedName": "OU=Facultad de Ingenieria Informatica,DC=cujae,DC=edu,DC=cu",
                 "name": "Facultad de Ingenieria Informatica"}]

    def dummy_buscarAreas_por_name(areas, area):
        raise requests.exceptions.ConnectionError("Error de conexión simulada")

    def dummy_buscarTrabajador_and_Estudiante(ci, areatemp):
        return [{"identification": ci, "area": "Facultad de Ingenieria Informatica",
                 "personType": "Student", "studentYear": "5", "name": "Juan", "surname": "Pérez", "lastname": "Gómez"}]

    def dummy_retreive_person(ci, db):
        return None  # Simula que la persona no existe previamente en la BD

    def dummy_get_carnet_by_person(ci, db):
        return None  # Simula que la persona no tiene un carnet previo

    def dummy_buscar_trabajador_con_cargo(ci, dbroles):
        return False

    def dummy_list_motivos(db):
        return ["Cambio de rol", "Nuevo Ingreso", "Cambio de Area"]

    def dummy_buscar_Tipo_Estudiante_carnet(ci):
        return "Seminterno"  # Simula que el estudiante tiene este tipo de carnet

    def dummy_buscar_buscar_personas_por_areas_ci(area: str, ci: str):
        # Simulación de respuesta esperada
        dummy_response = [
            {
                "identification": ci,
                "firstName": "Juan",
                "middleName": "Carlos",
                "lastName": "Pérez",
                "idCareer": area,
                "idCourseType": "Diurno",
                "idSex": "M",
                "idEntrySource": "Concurso",
                "idStudentStatus": "Activo",
                "personType": "Student",
                "studentType":"Seminterno",
                "area": "Facultad de Ingenieria Informatica"
            }
        ]

        # Simula convertir la respuesta en JSON como lo haría una solicitud real
        return json.loads(json.dumps(dummy_response))
    # Parches con monkeypatch
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_current_user_from_token", dummy_get_current_user_from_token)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas", dummy_buscarAreas)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarAreas_por_name", dummy_buscarAreas_por_name)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscarTrabajdor_and_Estudiante", dummy_buscarTrabajador_and_Estudiante)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.retreive_person", dummy_retreive_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.get_carnet_by_person", dummy_get_carnet_by_person)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.list_motivos", dummy_list_motivos)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_trabajador_con_cargo", dummy_buscar_trabajador_con_cargo)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_Tipo_Estudiante_carnet", dummy_buscar_Tipo_Estudiante_carnet)
    monkeypatch.setattr("webapp.crear_carnet.router_crear_matriculado.buscar_personas_por_areas_ci", dummy_buscar_buscar_personas_por_areas_ci)

    # Parámetros simulados
    area = "Facultad de Ingenieria Informatica"
    ci = "02032466727"

    # Cliente de prueba para FastAPI
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.cookies.set("access_token", fake_token)  # Simula token en cookies
        response = await client.get(f"/crearUnMatriculado/{area}/{ci}")

    # Verificaciones
    assert response.status_code == 503  # Verifica que devuelve correctamente el HTML
    assert response.json().get("detail") == "Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet."