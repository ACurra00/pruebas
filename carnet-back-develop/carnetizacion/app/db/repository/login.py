from db.models.usuario import Usuario
from sqlalchemy.orm import Session


def get_user(nombre_usuario: str, db: Session):
    user = db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()
    return user


def update_state_usuario_by_id(id: int, db: Session):
    exist_usuario = db.query(Usuario).filter(Usuario.id == id)
    if not exist_usuario.first():
        return 0
    exist_usuario.update({"is_activo": True})
    db.commit()
    return 1
