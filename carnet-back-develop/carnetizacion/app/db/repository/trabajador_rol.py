from sqlalchemy.orm import Session

from schemas.trabajador_rol import trabajador_rol_Create
from db.models.trabajador_rol import trabajador_rol


def create_new_trabajdor_rol(trabajador_rol: trabajador_rol_Create,db: Session):
    trabajador_rol_object = trabajador_rol(**trabajador_rol_Create.dict())
    db.add(trabajador_rol_object)
    db.commit()
    db.refresh(trabajador_rol_object)
    return trabajador_rol_object

#pendiente quedo esto aca