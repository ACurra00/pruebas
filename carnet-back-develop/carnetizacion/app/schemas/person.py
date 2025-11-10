from lib2to3.pgen2.token import OP
from typing import Optional

from pydantic import BaseModel


class PersonBase(BaseModel):
    ci: Optional[str] = None
    nombre: Optional[str] = None
    area: Optional[str] = None
    rol : Optional[str] = None

class PersonCreate(PersonBase):
    ci: str
    nombre: str
    area: str
    rol: str

class ShowPerson(PersonBase):
    ci: str
    nombre: str
    area: str
    rol: str
    is_activa: bool

    class Config:
        orm_mode = True