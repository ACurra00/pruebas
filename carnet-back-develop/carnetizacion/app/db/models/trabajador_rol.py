from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class TrbajadorRol(Base):
    id_trabajador_rol = Column(Integer, primary_key=True, index=True)
    person_ci = Column(String, ForeignKey("person.ci"))
    es_cuadro = Column(Boolean(), nullable=False)
    es_consejo_u = Column(Boolean(), nullable=False)
