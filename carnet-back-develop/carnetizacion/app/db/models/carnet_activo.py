
from datetime import datetime

from db.base_class import Base

from sqlalchemy import Column

from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime


class estado(str, Enum):
    Solicitado = "Solicitado"
    Hecho = "Hecho"
    Entregado = "Entregado"


class CarnetActivo(Base):
    id = Column(Integer, primary_key=True, index=True)
    person_ci = Column(String, ForeignKey("person.ci"))
    folio = Column(Integer, nullable=False)
    tipo_motivo_id = Column(Integer, ForeignKey("tipomotivo.id_motivo"))
    comprobante_motivo = Column(String)
    estado = Column(
        Enum("Solicitado", "Hecho", "Entregado", name="estado", create_type=True)
    )
    fecha = Column(DateTime, default=datetime.now)
    # foto = Column(String)
