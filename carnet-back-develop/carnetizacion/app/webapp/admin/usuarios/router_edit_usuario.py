import html
import requests
from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import retreive_usuario
from db.repository.usuario import update_usuario_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session
from schemas.usuario import UsuarioCreate
from webapp.admin.usuarios.form_ususarios import CrearUsuarioForm

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/usuario_admin/form_usuario/{id}")
async def edit_usuario(id: int, request: Request, db: Session = Depends(get_db)):
    print("Entra aqui a router edit user get")
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        usuario = retreive_usuario(id=id, db=db)
        response = templates.TemplateResponse(
            "admin/usuarios/crear_usuario.html",
            {"request": request, "usuario": usuario, "edit": True},
        )
        try:
            current_user: Usuario = get_current_user_from_token(param, db)
        except HTTPException:
            #print("Error al cargar el usuario, sera enviado al LOGIN")
            return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
        if (
            current_user.rol_usuario == "Administrador"
            or current_user.rol_usuario == "SuperAdmin"
        ):
            return response
        else:
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503,
                            detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        #print(e)
        return responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@router.post("/usuario_admin/form_usuario/{id}")
async def edit_usuario(id: int, request: Request, db: Session = Depends(get_db)):
  try:
    print("Entra aqui a router edit user post")
    form = CrearUsuarioForm(request)
    usuarioAnterior = retreive_usuario(id=id, db=db)
    await form.load_data()
    form.nombre_usuario = html.escape(usuarioAnterior.nombre_usuario)
    print("El nombre actual del usuario es ")
    print(form.nombre_usuario)
    if await form.is_valid():
        try:
            print("Entra al primer try")
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            response = responses.RedirectResponse(
                f"/usuario_admin", status_code=status.HTTP_302_FOUND
            )
            print("Coge bien el token")
            try:
                current_user: Usuario = get_current_user_from_token(param, db)
                print("Coge bien el usuario logueados")
            except HTTPException:
                #print("Error al cargar el usuario, sera enviado al LOGIN")
                return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
            if (
                current_user.rol_usuario == "Administrador"
                or current_user.rol_usuario == "SuperAdmin"
            ):
                print("Entra al if de admin")
                usuario = UsuarioCreate(**form.__dict__)
                update_usuario_by_id(id=id, usuario=usuario, db=db)
                username = current_user.nombre_usuario
                accion = "El usuario editó al usuario " + usuario.nombre_usuario
                tipo = "Gestionar usuarios"
                log = create_new_registro(db, username, accion, tipo)
                print("Edito el usuario y me va a redireccionar")
                return response
            else:
                return responses.RedirectResponse(
                    "/login", status_code=status.HTTP_302_FOUND
                )
        except HTTPException:
            #print(HTTPException)
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
  except requests.exceptions.ConnectionError as ce:
      raise HTTPException(status_code=503,
                          detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
