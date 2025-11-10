from typing import Optional

from db.models.usuario import rol_usuario
from pydantic import BaseModel


class UsuarioBase(BaseModel):
    nombre_usuario: Optional[str] = None
    rol_usuario: rol_usuario = None


class UsuarioCreate(UsuarioBase):
    nombre_usuario: str
    rol_usuario: rol_usuario


class ShowUsuario(UsuarioBase):
    nombre_usuario: str
    rol_usuario: rol_usuario
    is_activo: bool

    class Config:
        orm_mode = True
