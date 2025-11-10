from lib2to3.pgen2.token import OP
from typing import Optional

from pydantic import BaseModel


class Trabajador_rolBase(BaseModel):
    id_trabajador_rol: Optional[int] = None
    es_cuadro: Optional[bool] = False
    es_consejo_u: Optional[bool] = False
   

class trabajador_rol_Create(Trabajador_rolBase):
    id_trabajador_rol: int
    es_cuadro: bool
    es_consejo_u: bool

class ShowTrabjador_rol(Trabajador_rolBase):
    id_trabajador_rol: int
    es_cuadro: bool
    es_consejo_u: bool
