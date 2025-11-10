from typing import Optional
from db.models.carnet_activo import estado
from pydantic import BaseModel
from datetime import datetime


class CarnetActivoBase(BaseModel):
    folio: int
    comprobante_motivo: Optional[str] = None
    estado: estado = None
    fecha: datetime= datetime.now()

class CarnetActivoCreate(CarnetActivoBase):
    folio: int
    comprobante_motivo: str
    estado: estado
    fecha: datetime = datetime.now()

class ShowCarnetActivo(CarnetActivoBase):
    folio: int
    comprobante_motivo: str
    estado: estado
    fecha: datetime

    class Config:
        orm_mode = True
