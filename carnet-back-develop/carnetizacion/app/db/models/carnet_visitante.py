from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import DateTime
from datetime import date
from sqlalchemy.orm import relationship




class Carnet_visitante(Base):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    identificacion = Column(String(255), nullable=False)
    motivo_visita = Column(String(400), nullable=True)
    area_destino = Column(String(400), nullable=True)

    categoria_carnet = Column(Integer, ForeignKey("categoria_carnet_visitante.id"))
    categoria = relationship('Categoria_carnet_visitante', foreign_keys=[categoria_carnet])

    estado_carnet = Column(Integer, ForeignKey("estado_carnet_visitante.id"))
    estado = relationship('Estado_carnet_visitante', foreign_keys=[estado_carnet])

    folio = Column(String(255), nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=True)

