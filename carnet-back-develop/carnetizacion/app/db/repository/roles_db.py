from db.models.roles_db import Roles
from sqlalchemy.orm import Session


def get_trabajador_con_cargo(ci: str, db_roles: Session):
    trabajador_con_cargo = db_roles.query(Roles).filter(Roles.ci == ci).first()
    return trabajador_con_cargo