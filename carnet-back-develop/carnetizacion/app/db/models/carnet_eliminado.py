from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class CarnetEliminado(Base):
    id = Column(Integer, primary_key=True, index=True)
    person_ci = Column(String, ForeignKey("person.ci"))
    folio_desactivo = Column(Integer, nullable=False)
    area_anterior = Column(String, nullable=False)
    rol_anterior = Column(String, nullable=False)
