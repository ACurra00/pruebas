from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from schemas.carnet_activo import CarnetActivoCreate
from db.models.carnet_activo import CarnetActivo
from db.models.person import Person
from sqlalchemy import select
from datetime import datetime

def create_new_carnet_activo(carnet_activo: CarnetActivoCreate,db: Session,person_ci:int, tipo_motivo_id: int):
    carnet_activo_object = CarnetActivo(**carnet_activo.dict(),person_ci=person_ci, tipo_motivo_id= tipo_motivo_id)
    db.add(carnet_activo_object)
    db.commit()
    db.refresh(carnet_activo_object)
    return carnet_activo_object

def update_carnetactivo_by_ci(ci: str, carnet_actvivo: CarnetActivoCreate, db: Session):
    exist_carnetactivo = db.query(CarnetActivo).filter( CarnetActivo.person_ci == ci)
    if not exist_carnetactivo.first():
        return 0
    
    exist_carnetactivo.update(carnet_actvivo.__dict__)
    db.commit()
    return 1

def retreive_carnet(id:int,db:Session):
    item = db.query(CarnetActivo).filter(CarnetActivo.id == id).first()
    return item

def retrieve_all_carnets_by_date(fecha: date, db: Session):
    item = db.query(CarnetActivo).filter(CarnetActivo.fecha == fecha)
    return item


def lista_solicitado_filtrado_por_ci(db: Session, carnet_ci: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == carnet_ci).order_by(desc(CarnetActivo.id))
    return carnets

def lista_carnet_activo_x_ci(db: Session, carnet_ci: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.person_ci == carnet_ci).order_by(desc(CarnetActivo.id))
    return carnets
def lista_carnet_activo_x_nombre(db: Session, nombre: str):
    #name = nombre.upper()
    carnets = db.query(CarnetActivo).filter(CarnetActivo.person_ci == Person.ci, Person.nombre.ilike(f'%{nombre}%')).order_by(desc(CarnetActivo.id))

    for carnet in carnets:
        print(f"ID Carnet: {carnet.person_ci}")
        print(f"Folio: {carnet.folio}")
        print(f"Estado: {carnet.estado}")
        print(f"Fecha: {carnet.fecha}")

        # Obtener los detalles de la persona asociada al carnet
        person = db.query(Person).filter(Person.ci == carnet.person_ci).first()

        if person:
            print(f"Nombre: {person.nombre}")
            print(f"Área: {person.area}")
            print(f"Rol: {person.rol}")
        else:
            print("Persona no encontrada para este carnet")

        print("-" * 50)  # Separador entre carnets

    return carnets

def cambiar_estado (db: Session, estado:str, ci_carnet:str):
    exist_usuario = db.query(CarnetActivo).filter(CarnetActivo.person_ci == ci_carnet)
    if exist_usuario == []:
        return 0
    fecha = datetime.now()
    exist_usuario.update({"estado": estado,"fecha": fecha})

    db.commit()
    return exist_usuario

def cambiar_estado_por_cantidad(db: Session, estado:str, area:str, rol:str):
    list_usuarios = db.query(CarnetActivo).filter(CarnetActivo.person_ci == Person.ci, Person.rol.ilike(f'%{rol}%'),Person.area.ilike(f'%{area}%'))
    fecha = datetime.now()
    list_usuarios.update({"estado": estado,"fecha": fecha})

    db.commit()
    return list_usuarios

def lista_hechos_tipo(db: Session, tipo:str,area: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Hecho",CarnetActivo.person_ci == Person.ci, Person.rol.ilike(f'%{tipo}%'),Person.area.ilike(f'%{area}%')).order_by(desc(CarnetActivo.id))
    for carnet in carnets:
        print(f"ID Carnet: {carnet.person_ci}")
        print(f"Folio: {carnet.folio}")
        print(f"Estado: {carnet.estado}")
        print(f"Fecha: {carnet.fecha}")

        # Obtener los detalles de la persona asociada al carnet
        person = db.query(Person).filter(Person.ci == carnet.person_ci).first()

        if person:
            print(f"Nombre: {person.nombre}")
            print(f"Área: {person.area}")
            print(f"Rol: {person.rol}")
        else:
            print("Persona no encontrada para este carnet")

        print("-" * 50)  # Separador entre carnets
    return carnets

def lista_carnet_tipo(db: Session, tipo:str,area: str,estado):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == estado,CarnetActivo.person_ci == Person.ci, Person.rol.ilike(f'%{tipo}%'),Person.area.ilike(f'%{area}%')).order_by(desc(CarnetActivo.id))
    return carnets

def delete_carnet_activo(db: Session, ci_carnet:str):
    exist_usuario = db.query(CarnetActivo).filter(CarnetActivo.person_ci == ci_carnet)
    if not exist_usuario.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario:  {ci_carnet}  no existe",
        )
    exist_usuario.delete(synchronize_session= False)
    db.commit()
    return 0
def lista_solicitado_filtrado_por_area(db: Session, area: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.area == area).order_by(desc(CarnetActivo.id))
    return carnets

def lista_solicitados(db: Session):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Solicitado").order_by(desc(CarnetActivo.id))
    return carnets

def lista_solicitados_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Docente")
    results = db.execute(carnets).fetchall()
    
    return results

def lista_solicitados_no_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "No Docente")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_seminterno(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Seminterno")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_becado(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Nacional")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_becado_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Extranjero Convenio")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Extranjero")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_cuadros(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Cuadros")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_consejo(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Consejo Universitario")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_externo(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Externo")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitado_becado_asistido(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Nacional Asistido")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitado_extranjero_externo(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Solicitado", CarnetActivo.person_ci == Person.ci, Person.rol == "Extranjero Externo")
    results = db.execute(carnets).fetchall()
    return results

def lista_solicitados_filtrado_por_todos(db: Session, carnet_ci: str = None, area: str = None, nombre: str = None):
    query = db.query(CarnetActivo).distinct()
    if carnet_ci:
        query = query.filter(CarnetActivo.estado == "Solicitado",CarnetActivo.person_ci.ilike(f'%{carnet_ci}%'))
    if area:
        query = query.filter(CarnetActivo.estado == "Solicitado",CarnetActivo.person_ci == Person.ci, Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(CarnetActivo.estado == "Solicitado",CarnetActivo.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%'))
    
    carnets = query.filter(CarnetActivo.estado == "Solicitado").order_by(desc(CarnetActivo.id))
    return carnets

def get_carnet_by_person(person_ci: str,db: Session):
    carnet = db.query(CarnetActivo).filter(CarnetActivo.person_ci == person_ci).first()
    return carnet

def get_carnet_by_ci(db: Session, ci: str):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.person_ci == ci, Person.ci == ci)
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos(db: Session):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Hecho").order_by(desc(CarnetActivo.id))
    return carnets

def lista_hechos_filtrado_por_todos(db: Session, carnet_ci: str = None, area: str = None, nombre: str = None):
    query = db.query(CarnetActivo).distinct()
    if carnet_ci:
        query = query.filter(CarnetActivo.estado == "Hecho",CarnetActivo.person_ci.ilike(f'%{carnet_ci}%'))
    if area:
        query = query.filter(CarnetActivo.estado == "Hecho",CarnetActivo.person_ci == Person.ci, Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(CarnetActivo.estado == "Hecho",CarnetActivo.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%'))
    
    carnets = query.filter(CarnetActivo.estado == "Hecho").order_by(desc(CarnetActivo.id))
    
    return carnets
    
    
    
    
    
    
    
    
    

    
   
    




def lista_hechos_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "Docente")
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos_no_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "No Docente")
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos_seminterno(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "Seminterno")
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos_becado(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Nacional")
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos_becado_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Extranjero Convenio")
    results = db.execute(carnets).fetchall()
    return results

def lista_hechos_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Hecho", CarnetActivo.person_ci == Person.ci, Person.rol == "Extranjero")
    results = db.execute(carnets).fetchall()
    return results










def lista_entregados(db: Session):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Entregado").order_by(desc(CarnetActivo.id))
    return carnets
'''
def lista_entregados_filtrado_por_ci(db: Session, carnet_ci: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == carnet_ci).order_by(desc(CarnetActivo.id))
    return carnets

def lista_entregados_filtrado_por_area(db: Session, area: str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.area == area).order_by(desc(CarnetActivo.id))
    return carnets

def lista_entregados_filtrado_por_nombre(db: Session, nombre:str):
    carnets = db.query(CarnetActivo).filter(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%')).order_by(desc(CarnetActivo.id))
    return carnets
'''
def lista_entregados_filtrado_por_todos(db: Session, carnet_ci: str = None, area: str = None, nombre: str = None):
    query = db.query(CarnetActivo).distinct()
    if carnet_ci:
        query = query.filter(CarnetActivo.estado == "Entregado",CarnetActivo.person_ci.ilike(f'%{carnet_ci}%'))
    if area:
        query = query.filter(CarnetActivo.estado == "Entregado",CarnetActivo.person_ci == Person.ci, Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(CarnetActivo.estado == "Entregado",CarnetActivo.person_ci == Person.ci , Person.nombre.ilike(f'%{nombre}%'))

    carnets = query.filter(CarnetActivo.estado == "Entregado").order_by(desc(CarnetActivo.id))
    return carnets

def lista_entregados_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "Docente")
    results = db.execute(carnets).fetchall()
    return results

def lista_entregados_no_docente(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "No Docente")
    results = db.execute(carnets).fetchall()
    return results

def lista_entregados_seminterno(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "Seminterno")
    results = db.execute(carnets).fetchall()
    return results

def lista_entregados_becado(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Nacional")
    results = db.execute(carnets).fetchall()
    return results

def lista_entregados_becado_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "Becado Extranjero Convenio")
    results = db.execute(carnets).fetchall()
    return results

def lista_entregados_ex(db: Session):
    carnets = select(CarnetActivo, Person).where(CarnetActivo.estado == "Entregado", CarnetActivo.person_ci == Person.ci, Person.rol == "Extranjero")
    results = db.execute(carnets).fetchall()
    return results

def update_state_carnet(id: int, db: Session):
    exist_carnet = db.query(CarnetActivo).filter(CarnetActivo.id == id)
    if not exist_carnet.first():
        return 0
    exist_carnet.update({"estado": "Hecho"})
    db.commit()
    return 1

def update_folio_carnet(id: str, folio: int, db: Session):
    exist_carnet = db.query(CarnetActivo).filter(CarnetActivo.id == id)
    if not exist_carnet.first():
        return 0
    exist_carnet.update({"folio": folio})
    db.commit()
    return 1
