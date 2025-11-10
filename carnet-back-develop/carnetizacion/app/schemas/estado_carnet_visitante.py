from typing import Optional
from pydantic import BaseModel


class EstadoCarnetVisitanteBase(BaseModel):
    estado: Optional[str] = None
    descripcion: Optional[str] = None


class CreateEstadoCarnetVisitante(EstadoCarnetVisitanteBase):
    estado: str
    descripcion: str


class Show_EstadoCarnetVisitante(EstadoCarnetVisitanteBase):
    tipo_categoria: str
    descripcion: str

class EstadoCarnetVisitante(EstadoCarnetVisitanteBase):
    id: int

    class Config:
        orm_mode = True