from typing import Optional
from pydantic import BaseModel

class CarnetEliminadoBase(BaseModel):
    folio_desactivo : int
    area_anterior: Optional[str] = None
    rol_anterior: Optional[str] = None

class CarnetEliminadoCreate(CarnetEliminadoBase):
    folio_desactivo: int
    area_anterior: str
    rol_anterior: str

class ShowCarnetEliminado(CarnetEliminadoBase):
    folio_desactivo: int
    area_anterior: str
    rol_anterior: str

    class Config:
        orm_mode = True
