from typing import Optional
from pydantic import BaseModel


class CategoriaCarnetVisitanteBase(BaseModel):
    tipo_categoria: Optional[str] = None
    descripcion: Optional[str] = None


class CreateCategoriaCarnetVisitante(CategoriaCarnetVisitanteBase):
    tipo_categoria: str
    descripcion: str


class Show_CategoriaCarnetVisitante(CategoriaCarnetVisitanteBase):
    tipo_categoria: str
    descripcion: str

class CategoriaCarnetVisitante(CategoriaCarnetVisitanteBase):
    id: int

    class Config:
        orm_mode = True
