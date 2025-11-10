from typing import Optional

from db.models.ruta import tipo_ruta
from pydantic import BaseModel


class RutaBase(BaseModel):
    url: Optional[str] = None
    tipo_ruta: tipo_ruta = None


class RutaCreate(RutaBase):
    url: str
    tipo_ruta: tipo_ruta


class ShowRuta(RutaBase):
    url: str
    tipo_ruta: tipo_ruta

    class Config:
        orm_mode = True