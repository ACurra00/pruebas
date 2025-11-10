from typing import List
from typing import Optional
import html
from fastapi import Request


class CrearUsuarioForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.error_nombre_usuario: Optional[str] = ""
        self.nombre_usuario: Optional[str]
        self.rol_usuario: Optional[str]

    async def load_data(self):
        form = await self.request.form()
        self.nombre_usuario = form.get("nombre_usuario")
        if self.nombre_usuario is not None:
            self.nombre_usuario = html.escape(form.get("nombre_usuario"))
        self.rol_usuario = form.get("rol_usuario")
        if self.rol_usuario is not None:
            self.rol_usuario = html.escape(form.get("rol_usuario"))


    async def is_valid(self):
        if not self.nombre_usuario or self.nombre_usuario == "":
            self.error_nombre_usuario = "*Este campo es obligatorio"
            return False
        elif not self.rol_usuario or self.rol_usuario == "Seleccione":
            return False
        else:
            return True
