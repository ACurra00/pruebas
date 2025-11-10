from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class RegistroBase(BaseModel):
    username: Optional[str] = None
    accion: Optional[str] = None
    fecha: datetime = datetime.now()

class RegistroCreate(RegistroBase):
    username: str
    accion: str
    fecha: datetime = datetime.now()

class ShowRegistro(RegistroBase):
    username: str
    accion: str
    fecha: datetime

    class Config:
        orm_mode = True