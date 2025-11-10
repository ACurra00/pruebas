from typing import Optional
from pydantic import BaseModel


class Folio_ContBase(BaseModel):
    nombre_folio: str
    numero_1 : int
    numero_2 : int
    numero_3 : int
    numero_4 : int
    numero_5 : int
    cantidad_hojas: int

class Folio_ContCreate(Folio_ContBase):
    nombre_folio: str
    numero_1 : int
    numero_2 : int
    numero_3 : int
    numero_4 : int
    numero_5 : int
    cantidad_hojas: int

class ShowFolio_Cont(Folio_ContBase):
    nombre_folio: str
    numero_1 : int
    numero_2 : int
    numero_3 : int
    numero_4 : int
    numero_5 : int
    cantidad_hojas: int

