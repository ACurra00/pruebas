from locust import HttpUser, task, between

class CrearCarnetMatriculado(HttpUser):
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

    @task(2)
    def mostrar_crear_carnet(self):
        area = "Técnico Superior en Metrología (CCD)"
        ci = "05100166666"
        with self.client.get(f"/crearUnMatriculado/{area}/{ci}",
                              data={
                                  "rol": "Seminterno",
                                   "annoEstudiantePersona": 1,
                                   "nombre": "Darian",
                                  "ci": "02032466727",
                                  "comprobante_motivo": "ok",
                                  "tipoPersona": "Student",
                                  "area": "Facultad De Ingenieria En Automatica Y Biomedica",
                                  "area_anterior": "Facultad De Ingenieria En Automatica Y Biomedica",
                                  "rol_anterior": "Seminterno",
                                  "tipoMotivo": "Nuevo Ingreso"
                              },
                              cookies=self.cookies,
                              allow_redirects=False,
                              catch_response=True) as response:
            if response is None or response.url is None:
                response.failure("❌ Respuesta vacía o sin URL")
            elif "/login" in response.url or response.status_code == 302:
                response.failure("🔒 Redirigido a login al mostrar formulario")

    @task(2)
    def crear_carnet(self):
        area = "Técnico Superior en Metrología (CCD)"
        ci = "05100166666"

        with self.client.post(f"/crearUnMatriculado/{area}/{ci}", data={
            "tipoMotivo": "Reingreso",
            "comprobante_motivo": "ok",
        }, cookies=self.cookies, catch_response=True) as response:

            if response.status_code == 302 and "/login" in response.headers.get("Location", ""):
                response.failure("🔒 Redirigido a login: autenticación fallida")
            elif response.status_code == 200:
                response.success()
            else :
                response.failure(f"❌ Respuesta inesperada: {response.status_code}")
