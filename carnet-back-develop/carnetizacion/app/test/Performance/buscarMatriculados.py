from locust import HttpUser, task, between

class BuscarPersona(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Se ejecuta una vez por usuario al iniciar
        self.login()

    def login(self):
        response = self.client.post("/login", data={
            "username": "ceejesus",
            "password": "ce02032466727*"
        }, allow_redirects=False)

        # Si el login fue exitoso (redirección al home), guarda cookies
        if response.status_code in [200, 302]:
            self.cookies = response.cookies
        else:
            print("❌ Falló el login:", response.status_code)
            self.cookies = {}

    @task(2)
    def mostrar_buscar(self):
        with self.client.get("/matriculados/crear", cookies=self.cookies, catch_response=True) as response:
            if response is None or response.url is None:
                response.failure("❌ Respuesta vacía o sin URL")
            elif "/login" in response.url or response.status_code == 302:
                response.failure("🔒 Redirigido a login al mostrar formulario")

    @task(2)
    def buscar_persona(self):
        with self.client.post("/matriculados/crear", data={
            "areaBuscarPersona": "Ingeniería Informática (CD)",
            "tipoBuscarPersona": "carnet_x_lotes_on"
         }, cookies=self.cookies, catch_response=True) as response:
            if response is None or response.url is None:
                response.failure("❌ Respuesta vacía o sin URL")
            elif "/login" in response.url or response.status_code == 302:
                response.failure("🔒 Redirigido a login al hacer búsqueda")