from typing import List
from typing import Optional

from fastapi import Request


class ListaPersonaForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.seleccionar_todo: bool
        self.checkpersonas: bool
        self.imprimir: bool
        self.crear: bool
        self.cambiar_estado: bool

    async def load_data(self):
        form = await self.request.form()
        self.seleccionar_todo = form.get("seleccionar_todo")
        self.checkpersonas = form.get("checkpersonas")
        self.cambiar_estado = form.get("cambiar_estado")
        self.imprimir = form.get("imprimir")
        self.crear = form.get("crear")

    async def is_valid(self):
        if not self.checkpersonas:
            return True
        else:
            return False
