from locust import HttpUser, task, between

class BuscarPersona(HttpUser):
    wait_time = between(1, 3)  # Tiempo entre tareas por usuario

    @task(2)
    def mostrar_buscar(self):
        self.client.get("/")  # Muestra el formulario de buscar

    @task(2)
    def buscar_persona(self):
        self.client.post("/", data={
                "areaBuscarPersona": "Facultad de Ingenieria Informatica",
                "tipoBuscarPersona": "carnet_x_lotes_on",
                "tipoBuscarCarnet": "carnet_x_lotes_Estudiante",
                "student_year": "4"
            })  # Simula la busuqeda