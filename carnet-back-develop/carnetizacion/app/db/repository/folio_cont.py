from db.models.folio_cont import Folio_Cont
from schemas.folio_cont import Folio_ContCreate
from sqlalchemy.orm import Session


def create_folio_cont(folio_cont: Folio_ContCreate, db: Session):
    folio_cont_object = Folio_Cont(**folio_cont.dict())
    db.add(folio_cont_object)
    db.commit()
    db.refresh(folio_cont_object)
    return folio_cont_object


def buscar_folio_por_nombre(name: str, db: Session):
    
    item = db.query(Folio_Cont).filter(Folio_Cont.nombre_folio.ilike(f'%{name}%')).first()
    
    
    return item

def retreive_last_folio_cont(db: Session):
    item = db.query(Folio_Cont).order_by(Folio_Cont.id.desc()).first()
    return item

def update_folio_by_id(id: int, folio: Folio_ContCreate, db: Session):
    exist = db.query(Folio_Cont).filter(Folio_Cont.id == id)
    if not exist.first():
        return 0
    exist.update(folio.__dict__)
    db.commit()
    return 1

def update_folio_by_name(name: str, numero_1 :int,numero_2 :int , numero_3:int, numero_4:int, numero_5:int, cantidad_hojas:int, db: Session):
    exist = db.query(Folio_Cont).filter(Folio_Cont.nombre_folio.ilike(f'%{name}%'))
    #print(exist.first())
    #print(name)
    if not exist.first():      
        return 0
    if cantidad_hojas is None or cantidad_hojas == "":
        cantidad_hojas = 0
    exist.update({"numero_1": numero_1,
                  "numero_2": numero_2,
                  "numero_3": numero_3,
                  "numero_4": numero_4,
                  "numero_5": numero_5,
                  "cantidad_hojas": cantidad_hojas},
                 synchronize_session=False)
    db.commit()
    return 1

def update_folio_by_name_and_only_number(name: str, numero: int, column: int, db: Session):
    # Primero, verificamos si existe algún registro que coincida con el nombre dado
    exist = db.query(Folio_Cont).filter(Folio_Cont.nombre_folio.ilike(f'%{name}%')).first()

    # Si no existe tal registro, retornamos 0 indicando que no se encontró ningún registro para actualizar
    if not exist:
        return 0

    # Preparamos el diccionario de actualización basado en el valor de 'column'
    update_dict = {}
    if column == 0:
        update_dict["numero_1"] = numero
    elif column == 1:
        update_dict["numero_2"] = numero
    elif column == 2:
        update_dict["numero_3"] = numero
    elif column == 3:
        update_dict["numero_4"] = numero
    elif column == 4:
        update_dict["numero_5"] = numero

    # Realizamos la actualización en la base de datos
    db.query(Folio_Cont).filter(Folio_Cont.nombre_folio.ilike(f'%{name}%')).update(update_dict,
                                                                                    synchronize_session='fetch')

    # Confirmamos los cambios
    db.commit()

    return 1