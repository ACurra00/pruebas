from enum import unique
from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class TipoMotivo(Base):
    id_motivo = Column(Integer, primary_key=True, nullable=False, index=True)
    nombre_motivo = Column(String, nullable=False, unique=True)
