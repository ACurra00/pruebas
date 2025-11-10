from typing import List
from typing import Optional
import html
from fastapi import Request


class BuscarPersonaForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errorCI: Optional[str] = ""
        self.users: List
        self.errorArea: Optional[str]= ""
        self.ciBuscarPersona: Optional[str]
        self.areaBuscarPersona: Optional[str]
        self.tipoBuscarPersona: Optional[str]
        self.tipoBuscarCarnet: Optional[str]
        self.student_year: Optional[str]
        self.errorTipo: Optional[str]
        self.errorFiltro: Optional[str]
        self.erroryear: Optional[str]

    async def load_data(self):
        form = await self.request.form()
        self.ciBuscarPersona = form.get("ciBuscarPersona")
        if self.ciBuscarPersona is not None:
            self.ciBuscarPersona = html.escape(form.get("ciBuscarPersona"))
        self.areaBuscarPersona = html.escape(form.get("areaBuscarPersona"))
        self.tipoBuscarPersona = form.get("tipoBuscarPersona")
        if self.tipoBuscarPersona is not None:
            self.tipoBuscarPersona = html.escape(form.get("tipoBuscarPersona"))
        self.tipoBuscarCarnet = form.get("tipoBuscarCarnet")
        if self.tipoBuscarCarnet is not None:
            self.tipoBuscarCarnet = html.escape(form.get("tipoBuscarCarnet"))
        self.student_year = form.get("student_year")
        if self.student_year is not None:
            self.student_year = html.escape(form.get("student_year"))
        

    def is_valid(self):
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
        if self.tipoBuscarPersona == "carnet_x_lotes_off": # no es por lotes
            if  not len(self.ciBuscarPersona) == 11:
                self.errorCI = "*Un Carnet de Identidad no valido"
                result = False
        elif self.tipoBuscarCarnet == "Seleccione":
            result = False
            self.errorFiltro= "*Seleccione un tipo de persona válido"
            self.erroryear=""
      
        if self.student_year == "Seleccione" and self.tipoBuscarCarnet == "carnet_x_lotes_Estudiante":
                result = False
                self.errorFiltro=""
                self.erroryear =  "*Seleccione un año de estudiante válido"
    
        return result
    
    def is_carntet_x_lotes(self):
        result = True
        if self.areaBuscarPersona == "Seleccione":
            self.errorArea = "*Este campo es obligatorio"
            result = False
        if self.tipoBuscarPersona == "Seleccione":
            self.errorTipo = "*Este campo es obligatorio"
            result = False

        return result


     