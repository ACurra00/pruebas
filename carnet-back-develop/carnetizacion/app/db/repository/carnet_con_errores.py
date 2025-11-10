from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy import select
from db.models.carnet_con_errores import carnet_con_errores
from schemas.carnet_con_errores import CreateCarnet_con_errores
from db.models.person import Person



def create_new_carnet_con_errores(carnet_con_error: CreateCarnet_con_errores,db: Session):

    carnet_con_errores_object = carnet_con_errores(**carnet_con_error.dict(),)
    db.add(carnet_con_errores_object)
    db.commit()
    db.refresh(carnet_con_errores_object)
    return carnet_con_errores_object

def lista_carnet_con_errores(db: Session):
    carnets = db.query(carnet_con_errores).order_by(desc(carnet_con_errores.id))
    return carnets

def lista_con_errores_filtrado_por_ci(db: Session, carnet_ci: str):
    carnets = db.query(carnet_con_errores).filter(carnet_con_errores.persona_ci == carnet_ci).order_by(desc(carnet_con_errores.id))
    return carnets

def lista_con_errores_filtrado_por_area(db: Session, area: str):
    carnets = db.query(carnet_con_errores).filter(carnet_con_errores.persona_ci == Person.ci, Person.area == area).order_by(desc(carnet_con_errores.id))
    return carnets

def lista_con_errores_filtrado_por_nombre(db: Session, nombre: str):
    carnets = db.query(carnet_con_errores).filter(carnet_con_errores.persona_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%')).order_by(desc(carnet_con_errores.id))
    return carnets

def lista_con_errores_filtrado_por_todos(db: Session, carnet_ci: str = None, area: str = None, nombre: str = None):
    query = db.query(carnet_con_errores).distinct()
    print("El area es ")
    print(area)
    print("EL nombre es ")
    print(nombre)
    if carnet_ci:
        query = query.filter(carnet_con_errores.persona_ci.ilike(f'%{carnet_ci}%'))
    if area:
        query = query.filter(carnet_con_errores.persona_ci == Person.ci, Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(carnet_con_errores.persona_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%'))
    carnets = query.order_by(desc(carnet_con_errores.id))
    return carnets