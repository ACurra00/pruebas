from typing import List
from typing import Optional
import html
from fastapi import Request


class FolioForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.cont_folio_numero_1: int
        self.cont_folio_numero_2:int
        self.cont_folio_numero_3:int
        self.cont_folio_numero_4:int
        self.cont_folio_numero_5:int
        self.cont_cantidad_hojas: int

        self.errorfolio_numero_1: Optional[str] = ""
        self.errorfolio_numero_2: Optional[str] = ""
        self.errorfolio_numero_3: Optional[str] = ""
        self.errorfolio_numero_4: Optional[str] = ""
        self.errorfolio_numero_5: Optional[str] = ""
        self.errorCantidad_hojas: Optional[str] = ""
        

    async def load_data(self):
        form = await self.request.form()

        self.cont_folio_numero_1 = form.get("cont_folio_numero_1")
        if self.cont_folio_numero_1 is not None:
            self.cont_folio_numero_1 = html.escape(form.get("cont_folio_numero_1"))
        self.cont_folio_numero_2= form.get("cont_folio_numero_2")
        if self.cont_folio_numero_2 is not None:
            self.cont_folio_numero_2 = html.escape(form.get("cont_folio_numero_2"))
        self.cont_folio_numero_3= form.get("cont_folio_numero_3")
        if self.cont_folio_numero_3 is not None:
            self.cont_folio_numero_3 = html.escape(form.get("cont_folio_numero_3"))
        self.cont_folio_numero_4= form.get("cont_folio_numero_4")
        if self.cont_folio_numero_4 is not None:
            self.cont_folio_numero_4 = html.escape(form.get("cont_folio_numero_4"))
        self.cont_folio_numero_5= form.get("cont_folio_numero_5")
        if self.cont_folio_numero_5 is not None:
            self.cont_folio_numero_5 = html.escape(form.get("cont_folio_numero_5"))
        self.cont_cantidad_hojas= form.get("cont_cantidad_hojas")
        if self.cont_cantidad_hojas is not None:
            self.cont_cantidad_hojas = html.escape(form.get("cont_cantidad_hojas"))
        
        
    async def is_valid(self):
        error = True
        if not self.cont_folio_numero_1:
            self.errorfolio_numero_1="Folio numero 1 es requerido"
            error = False
        if self.cont_folio_numero_1 <0:
            self.errorfolio_numero_1 = "El folio debe ser mayor que 0"
            error = False
        
        if not self.cont_folio_numero_2:
            self.errorfolio_numero_2="Folio numero 2 es requerido"
            error = False
        if self.cont_folio_numero_2 <0:
            self.errorfolio_numero_2 = "El Folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_3:
            self.errorfolio_numero_3="Folio numero 3 es requerido"
            error = False
        if self.cont_folio_numero_3 <0:
            self.errorfolio_numero_3 = "El folio debe ser mayor que 0"
            error = False

        if not self.cont_folio_numero_4:
            self.errorfolio_numero_4="Folio numero 4 es requerido"
            error = False
        if self.cont_folio_numero_4 <0:
            self.errorfolio_numero_4 = "El folio debe ser mayor que 0"
            error = False
        
        if not self.cont_folio_numero_5:
            self.errorfolio_numero_5="Folio numero 5 es requerido"
            error = False
        if self.cont_folio_numero_5 <0:
            self.errorfolio_numero_5 = "El folio debe ser mayor que 0"
            error = False

        if self.cont_cantidad_hojas >0:
            self.errorCantidad_hojas = "La Cantidad de Hojas debe ser mayor que 0"
            error = False

        if error:
            return True
        
        return False
