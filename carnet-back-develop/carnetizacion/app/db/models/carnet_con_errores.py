from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from datetime import datetime


class carnet_con_errores(Base):
    id = Column(Integer, primary_key=True, index=True)
    persona_ci = Column(String, nullable = False)
    area_con_error = Column(String, nullable=False)
    error = Column(String,nullable=False)
    fecha_error  = Column(DateTime, default=datetime.now)
    nombre_con_error = Column(String, nullable=False)
    error_simple= Column(String, nullable=False)