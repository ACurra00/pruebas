from locust import HttpUser, task, between

class UsuarioDelSistema(HttpUser):
    wait_time = between(1, 3)  # Tiempo entre tareas por usuario

    @task(2)
    def acceder_al_login(self):
        self.client.get("/")  # Muestra el formulario de buscar persona

    @task(2)
    def autenticarse(self):
        self.client.post("/", data={
            "username": "ceejesus",
            "password": "ce02032466727*"
        })  # Simula busca personas

