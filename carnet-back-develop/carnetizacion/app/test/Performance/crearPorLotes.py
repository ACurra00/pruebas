from locust import HttpUser, task, between

class CrearCarnetXLotes(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/login", data={
            "username": "ceejesus",
            "password": "ce02032466727*"
        }, allow_redirects=False)

        if response.status_code in [200, 302]:
            self.cookies = response.cookies
        else:
            print("❌ Falló el login:", response.status_code)
            self.cookies = {}

    @task(1)
    def crear_carnet_lotes(self):
        area = "DG de ICI Area Central"
        tipo = "carnet_x_lotes_Docente"
        year = None

        with self.client.get(f"/carnetXLotes/{area}/{tipo}/{year}",
                             cookies=self.cookies,
                             allow_redirects=False,
                             catch_response=True) as response:
            if response.status_code == 302 and "/carnets/solicitados" in response.headers.get("Location", ""):
                response.success()
            elif response.status_code == 302 and "/login" in response.headers.get("Location", ""):
                response.failure("🔒 Redirigido a login: autenticación fallida")
            else:
                response.failure(f"❌ Código inesperado: {response.status_code}")