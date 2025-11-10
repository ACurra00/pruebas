import json

from fastapi import status
from starlette import responses


def test_create_motivo(client):
    data = {"nombre_motivo": "Cambio de rol"}
    response = client.post("/motivos/create-motivo/", json.dumps(data))
    assert response.status_code == 200
    assert response.json()["nombre_motivo"] == "Cambio de rol"


def test_read_motivo(client):
    data = {"nombre_motivo": "Cambio de rol"}
    response = client.post("/motivos/create-motivo/", json.dumps(data))
    response = client.get("/motivos/get/1/")
    assert response.status_code == 200
    assert response.json()["nombre_motivo"] == "Cambio de rol"


def test_read_all_motivos(client):
    data = {"nombre_motivo": "Cambio de rol"}
    client.post("/motivos/create-motivo/", json.dumps(data))
    client.post("/motivos/create-motivo/", json.dumps(data))

    response = client.get("/motivos/all/")
    assert response.status_code == 200
    assert response.json()[0]
    assert response.json()[1]


def test_delete_tipo_motivo(client):
    data = {"nombre_motivo": "Cambio de rol"}
    client.post("/motivos/create-motivo/", json.dumps(data))
    msg = client.delete("/motivos/delete/1")
    response = client.get("/motivos/get/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_motivo(client):
    data = {"nombre_motivo": "Cambio de rol"}
    client.post("/motivos/create-motivo/", json.dumps(data))
    data["nombre_motivo"] = "Cambio de area"
    response = client.put("/motivos/update/1", json.dumps(data))
    assert response.json()["msg"] == "Successfully updated data."
