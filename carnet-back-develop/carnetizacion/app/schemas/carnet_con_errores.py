from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class carnet_con_errores(BaseModel):
    persona_ci : Optional[str] = None
    area_con_error: Optional[str] = None
    error: Optional[str] = None
    fecha_error: datetime= datetime.now()
    nombre_con_error: Optional[str] = None
    error_simple : Optional[str] = None

class CreateCarnet_con_errores(carnet_con_errores):
    persona_ci: str
    area_con_error: str
    error: str
    fecha_error : datetime
    nombre_con_error: str
    error_simple: str

class ShowCarnet_con_errores(carnet_con_errores):
    persona_ci: str
    area_con_error: str
    error: str
    fecha_error : datetime
    nombre_con_error: str
    error_simple: str
    
    class Config:
        orm_mode = True