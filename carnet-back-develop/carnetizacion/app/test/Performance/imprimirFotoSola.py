from locust import HttpUser, task, between

class UsuarioCarnet(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login y paso intermedio obligatorio
        self.login()
        self.preparar_creacion_lotes()

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

    def preparar_creacion_lotes(self):
        # Paso intermedio necesario antes de imprimir
        area = "DG de ICI Area Central"
        tipo = "carnet_x_lotes_Docente"
        year = None

        with self.client.get(f"/carnetXLotes/{area}/{tipo}/{year}",
                             cookies=self.cookies,
                             allow_redirects=False,
                             catch_response=True) as response:
            location = response.headers.get("Location", "")
            if response.status_code == 302 and "/carnets/solicitados" in location:
                response.success()
            elif response.status_code == 302 and "/login" in location:
                response.failure("🔒 Redirigido a login: autenticación fallida")
            else:
                response.failure(f"❌ Código inesperado en paso intermedio: {response.status_code}")

    @task(1)
    def imprimir_carnets_solicitados(self):
        # Esta es la prueba objetivo
        with self.client.get("/carnets/solicitados?imprimir=true&carnet_id=91011139059",
                             cookies=self.cookies,
                             allow_redirects=False,
                             catch_response=True) as response:

            location = response.headers.get("Location", "")
            status = response.status_code

            if status == 200:
                response.success()
            elif status == 302:
                if "/login" in location:
                    response.failure("🔒 Redirigido a login: sesión no válida")
                else:
                    response.failure(f"🔁 Redirección inesperada a: {location}")
            else:
                response.failure(f"❌ Código inesperado: {status}")