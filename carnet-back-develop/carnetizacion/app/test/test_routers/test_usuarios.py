import json


def test_create_user(client):
    data = {"nombre_usuario": "testuser", "rol_usuario": "Carnetizador"}
    response = client.post("/usuarios/create_usuario/", json.dumps(data))
    assert response.status_code == 200
    assert response.json()["nombre_usuario"] == "testuser"
    assert response.json()["is_activo"] == True
