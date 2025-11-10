from unicodedata import name

from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String


class rol_usuario(str, Enum):
    Carnetizador = "Carnetizador"
    Administrador = "Administrador"
    SuperAdmin = "SuperAdmin",
    Recepcionista = 'Recepcionista'


class Usuario(Base):
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, nullable=False)
    is_activo = Column(Boolean(), default=False)
    rol_usuario = Column(
        Enum(
            "Carnetizador",
            "Administrador",
            "SuperAdmin",
            "Recepcionista",
            name="rol_usuario",
            create_type=False,
        )
    )
