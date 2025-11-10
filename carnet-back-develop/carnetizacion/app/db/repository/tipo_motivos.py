from db.models.tipo_motivo import TipoMotivo
from schemas.tipo_motivo import TipoMotivoCreate
from sqlalchemy.orm import Session


def create_tipo_motivo(tipo_motivo: TipoMotivoCreate, db: Session):
    tipo_motivo_object = TipoMotivo(**tipo_motivo.dict())
    db.add(tipo_motivo_object)
    db.commit()
    db.refresh(tipo_motivo_object)
    return tipo_motivo_object


def retreive_motivo(id: int, db: Session):
    item = db.query(TipoMotivo).filter(TipoMotivo.id_motivo == id).first()
    return item

# def retreive_motivo_by_name(nombre_motivo: str, db: Session):
#     item = db.query(TipoMotivo).filter(TipoMotivo.nombre_motivo == nombre_motivo).first()
#     return item


def list_motivos(db: Session):
    motivos = db.query(TipoMotivo).all()
    return motivos


def update_motivo_by_id(id: int, tipo_motivo: TipoMotivoCreate, db: Session):
    exist_motivo = db.query(TipoMotivo).filter(TipoMotivo.id_motivo == id)
    if not exist_motivo.first():
        return 0
    exist_motivo.update(tipo_motivo.__dict__)
    db.commit()
    return 1


def delete_tipo_motivo_by_id(id: int, db: Session):
    existing_motivo = db.query(TipoMotivo).filter(TipoMotivo.id_motivo == id)
    if existing_motivo == []:
        return 0
    existing_motivo.delete(synchronize_session=False)
    db.commit()
    return 1
