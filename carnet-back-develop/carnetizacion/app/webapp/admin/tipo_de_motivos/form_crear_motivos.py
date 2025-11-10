from typing import List
from typing import Optional
import html
from fastapi import Request


class CrearMotivoForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.error_nombre_motivo: Optional[str] = ""
        self.nombre_motivo: Optional[str]

    async def load_data(self):
        form = await self.request.form()
        self.nombre_motivo = form.get("nombre_motivo")
        if self.nombre_motivo is not None:
            self.nombre_motivo = html.escape(form.get("nombre_motivo"))
        #print(self.nombre_motivo)

    async def is_valid(self):
        if not self.nombre_motivo or self.nombre_motivo == "":
            self.error_nombre_motivo = "*Este campo es obligatorio"
            return False
        else:
            return True
