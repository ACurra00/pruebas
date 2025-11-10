from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

class Categoria_carnet_visitante(Base):
    id = Column(Integer, primary_key=True)
    tipo_categoria = Column(String(255), nullable=False)
    descripcion = Column(String(400), nullable=False)
    