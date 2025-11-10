from schemas.ruta import RutaCreate
from sqlalchemy.orm import Session
from db.models.ruta import Ruta

def create_new_ruta(ruta: RutaCreate, db: Session):
    ruta_n = Ruta(
        url=ruta.url,
        tipo_ruta = ruta.tipo_ruta
    )
    db.add(ruta_n)
    db.commit()
    db.refresh(ruta_n)
    return ruta_n


def lista_rutas(db: Session):
    rutas = db.query(Ruta).all()
    return rutas


def retreive_ruta(id: int, db: Session):
    item = db.query(Ruta).filter(Ruta.id == id).first()
    return item


def update_ruta_by_id(id: int, ruta: RutaCreate, db: Session):
    exist_ruta = db.query(Ruta).filter(Ruta.id == id)
    if not exist_ruta.first():
        return 0
    exist_ruta.update(ruta.__dict__)
    db.commit()
    return 1


def delete_ruta_by_id(id: int, db: Session):
    existing_ruta = db.query(Ruta).filter(Ruta.id == id)
    if not existing_ruta.first():
        return 0
    existing_ruta.delete(synchronize_session=False)
    db.commit()
    return 1