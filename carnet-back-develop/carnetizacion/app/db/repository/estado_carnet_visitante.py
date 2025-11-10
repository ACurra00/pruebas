from sqlalchemy.orm import Session
from schemas.estado_carnet_visitante import EstadoCarnetVisitante, CreateEstadoCarnetVisitante
from db.models.estado_carnet_visitante import Estado_carnet_visitante


def get_estados(db: Session, skip: int = 0, limit: int = 100000000):
    return db.query(Estado_carnet_visitante).offset(skip).limit(limit).all()