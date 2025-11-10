from sqlalchemy.orm import Session
from sqlalchemy import desc

from schemas.carnet_eliminado import CarnetEliminadoCreate
from db.models.carnet_eliminado import CarnetEliminado
from db.models.person import Person

def create_new_carnet_eliminado(carnet_eliminado: CarnetEliminadoCreate,db: Session,person_ci:int):

    carnet_eliminado_object = CarnetEliminado(**carnet_eliminado.dict(),person_ci=person_ci)
    db.add(carnet_eliminado_object)
    db.commit()
    db.refresh(carnet_eliminado_object)
    return carnet_eliminado_object

def lista_eliminados(db: Session):
    carnets = db.query(CarnetEliminado).order_by(desc(CarnetEliminado.id))
    return carnets

def lista_eliminados_array(db: Session):
    carnets = db.query(CarnetEliminado).order_by(desc(CarnetEliminado.id)).all()
    return carnets

def eliminar_eliminados(db: Session):
    db.query(CarnetEliminado).delete()
    db.commit()

def lista_eliminados_filtrado_por_ci(db: Session, carnet_ci: str):
    carnets = db.query(CarnetEliminado).filter(CarnetEliminado.person_ci == carnet_ci).order_by(desc(CarnetEliminado.id))
    return carnets

def lista_eliminados_filtrado_por_area(db: Session, area: str):
    carnets = db.query(CarnetEliminado).filter(CarnetEliminado.person_ci == Person.ci, Person.area == area).order_by(desc(CarnetEliminado.id))
    return carnets

def lista_eliminados_filtrado_por_nombre(db: Session, nombre:str):
    carnets = db.query(CarnetEliminado).filter(CarnetEliminado.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%')).order_by(desc(CarnetEliminado.id))
    return carnets


def lista_eliminados_filtrado_por_todos(db: Session, carnet_ci: str = None, area: str = None, nombre: str = None):
    query = db.query(CarnetEliminado)
    if carnet_ci:
        query = query.filter(CarnetEliminado.person_ci.ilike(f'%{carnet_ci}%'))
    if area:
        query = query.filter(CarnetEliminado.person_ci == Person.ci, Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(CarnetEliminado.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%'))
    carnets = query.order_by(desc(CarnetEliminado.id))
    return carnets