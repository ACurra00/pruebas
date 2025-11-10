from sqlalchemy.orm import Session
from db.models.carnet_activo import CarnetActivo
from schemas.person import PersonCreate
from db.models.person import Person


def create_new_person(person: PersonCreate,db: Session):
    person_object = Person(**person.dict())
    db.add(person_object)
    db.commit()
    db.refresh(person_object)
    return person_object

def retreive_person(ci: str, db: Session):
    item = db.query(Person).filter(Person.ci == ci).first()
    return item

def list_personas_por_ci(db: Session, ci:str):
    persons = db.query(Person).filter(Person.ci == ci)
    return persons

def list_personas_por_area(db: Session, area:str):
    persons = db.query(Person).filter(Person.area == area)
    return persons

def list_personas_por_area_tipo(db: Session, area:str,tipo:str):
    persons = db.query(Person).filter(Person.ci == CarnetActivo.person_ci, Person.rol.ilike(f'%{tipo}%'),Person.area.ilike(f'%{area}%'))

    # Imprimir los campos de cada objeto antes de devolverlo
    for person in persons:
        print(f"CI: {person.ci}")
        print(f"Nombre: {person.nombre}")
        print(f"Área: {person.area}")
        print(f"Rol: {person.rol}")

        # Imprimir si la persona está activa o no
        if person.is_activa:
            print("Persona está activa")
        else:
            print("Persona no está activa")

        print("-" * 50)  # Separador entre personas

    return persons


def list_personas_por_nombre(db: Session, nombre:str):
    persons = db.query(Person).filter(Person.nombre.ilike(f'%{nombre}%'))

    for person in persons:
        print(f"CI: {person.ci}")
        print(f"Nombre: {person.nombre}")
        print(f"Área: {person.area}")
        print(f"Rol: {person.rol}")

        # Imprimir si la persona está activa o no
        if person.is_activa:
            print("Persona está activa")
        else:
            print("Persona no está activa")

        print("-" * 50)  # Separador entre personas

    return persons

def list_personas_por_todos(db: Session, ci: str = None, area: str = None, nombre: str = None):
    query = db.query(Person)
    if ci:
        query = query.filter(Person.ci.ilike(f'%{ci}%'))
    if area:
        query = query.filter(Person.area.ilike(f'%{area}%'))
    if nombre:
        query = query.filter(Person.nombre.ilike(f'%{nombre}%'))
    persons = query.all()
    return persons



def list_persons(db: Session):
    persons = db.query(Person).all()
    return persons

# def list_persons_docente(db: Session):
#     persons = db.query(Person).filter(Person.rol == "Docente")
#     return persons


def update_person_by_ci(ci: str, person: PersonCreate, db: Session):
    exist_person = db.query(Person).filter(Person.ci == ci)
    if not exist_person.first():
        return 0
    
    exist_person.update(person.__dict__)
    db.commit()
    return 1