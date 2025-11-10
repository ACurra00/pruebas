from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Person(Base):
    
    ci = Column(String, nullable=False, primary_key=True)
    nombre = Column(String, nullable=False)
    is_activa = Column(Boolean(), default=True)
    area = Column(String, nullable=False)
    rol = Column(String, nullable=False)
    # carnet = Column(Integer, ForeignKey("carnetactivo.id"))
