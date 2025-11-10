from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

class Estado_carnet_visitante(Base):
    id = Column(Integer, primary_key=True)
    estado = Column(String(255), nullable=False)
    descripcion = Column(String(400), nullable=False)

