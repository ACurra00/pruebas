from db.base_class import Base
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String

class tipo_ruta(str, Enum):
    Contacto = "Contacto"
    Pie= "Pie de página"

class Ruta(Base):
    id_ruta = Column(Integer, primary_key=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    tipo_ruta=Column(
        Enum(
            "Contacto",
            "Pie de página",
            name="tipo_ruta",
            create_type=False,
        )
    )
