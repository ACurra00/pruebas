from typing import Optional

from pydantic import BaseModel


class TipoMotivoBase(BaseModel):
    nombre_motivo: Optional[str] = None


class TipoMotivoCreate(TipoMotivoBase):
    nombre_motivo: str


class ShowTipoMotivo(TipoMotivoBase):
    nombre_motivo: str

    class Config:
        orm_mode = True
