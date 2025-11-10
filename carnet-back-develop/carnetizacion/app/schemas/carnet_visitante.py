from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CarnetVisitanteBase(BaseModel):
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    motivo_visita: Optional[str] = None
    area_destino: Optional[str] = None
    categoria_carnet: int
    estado_carnet: int
    folio: Optional[str] = None
    fecha_entrada: datetime


class CreateCarnetVisitante(CarnetVisitanteBase):
    nombre: str
    identificacion: str
    motivo_visita: str
    area_destino: str
    categoria_carnet: int
    estado_carnet: int
    folio: str
    fecha_entrada: datetime


class Show_CarnetVisitante(CarnetVisitanteBase):
    nombre: str
    identificacion: str
    motivo_visita: str
    area_destino: str
    categoria_carnet: int
    estado_carnet: int
    folio: str
    fecha_entrada: datetime

class CarnetVisitante(CarnetVisitanteBase):
    id: int

    class Config:
        orm_mode = True