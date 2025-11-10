from enum import unique
from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime

class Registro(Base):
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    username = Column(String, nullable=False, unique=True)
    accion = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.now)