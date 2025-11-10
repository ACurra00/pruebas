from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String

class Folio_Cont(Base):
    id = Column(Integer, primary_key=True, index=True)
    nombre_folio = Column(String, nullable=False)
    numero_1 = Column(Integer, nullable=False)
    numero_2 = Column(Integer, nullable=False)
    numero_3 = Column(Integer, nullable=False)
    numero_4 = Column(Integer, nullable=False)
    numero_5 = Column(Integer, nullable=False)
    cantidad_hojas = Column(Integer, nullable=False)
    
    
    
