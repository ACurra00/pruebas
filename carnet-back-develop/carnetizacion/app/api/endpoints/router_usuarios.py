from db.repository.usuario import create_new_user
from db.repository.usuario import delete_usuario_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from schemas.usuario import ShowUsuario
from schemas.usuario import UsuarioCreate
from sqlalchemy.orm import Session
import requests
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import retreive_usuario

from db.repository.registro import create_new_registro

router = APIRouter()


@router.post("/create_usuario/", response_model=ShowUsuario)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    user = create_new_user(user=user, db=db)
    return user


@router.delete("/delete_usuario/{id}")
def delete_usuario(id: int, request: Request, db: Session = Depends(get_db)):
    usuario = retreive_usuario(id, db)
    nombre = usuario.nombre_usuario
    message = delete_usuario_by_id(id=id, db=db)
    message = delete_usuario_by_id(id=id, db=db)
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    username = current_user.nombre_usuario
    accion = "El usuario eliminó al usuario " + nombre
    tipo = "Gestionar usuarios"
    log = create_new_registro(db, username, accion, tipo)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {id} no existe",
        )
    return {"detail": "Eliminado completamente."}
