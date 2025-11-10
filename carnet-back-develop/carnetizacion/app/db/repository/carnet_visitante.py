from sqlalchemy.orm import Session
from schemas.carnet_visitante import CarnetVisitante, CreateCarnetVisitante
from db.models.carnet_visitante import Carnet_visitante


def get_visitantes(db: Session, skip: int = 0, limit: int = 100000000):
    return db.query(Carnet_visitante).offset(skip).limit(limit).all()

def create_visitante(db: Session, carnet_visitante: CreateCarnetVisitante):
    db_carnet_visitante = Carnet_visitante(nombre=carnet_visitante.nombre, identificacion=carnet_visitante.identificacion, motivo_visita=carnet_visitante.motivo_visita, area_destino=carnet_visitante.area_destino, categoria_carnet=carnet_visitante.categoria_carnet, estado_carnet=carnet_visitante.estado_carnet, folio=carnet_visitante.folio, fecha_entrada=carnet_visitante.fecha_entrada, fecha_salida=carnet_visitante.fecha_salida)
    db.add(db_carnet_visitante)
    db.commit()
