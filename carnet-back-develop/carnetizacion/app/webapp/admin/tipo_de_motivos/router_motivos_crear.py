from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.tipo_motivos import create_tipo_motivo
from db.repository.tipo_motivos import list_motivos
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
from schemas.tipo_motivo import TipoMotivoCreate
from webapp.admin.tipo_de_motivos.form_crear_motivos import CrearMotivoForm
from db.repository.registro import create_new_registro
from schemas.registro import RegistroCreate
import requests

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/motivos_admin/crear-motivo")
async def motivos_crear(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        tipo_motivo = ""
        response = templates.TemplateResponse(
            "admin/motivos/crear_motivos.html",
            {"request": request, "tipo_motivo": tipo_motivo},
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


@router.post("/motivos_admin/crear-motivo")
async def motivos_crear(request: Request, db: Session = Depends(get_db)):
 try:
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    form = CrearMotivoForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            current_user: Usuario = get_current_user_from_token(param, db)
            response = responses.RedirectResponse(
                f"/motivos_admin", status_code=status.HTTP_302_FOUND
            )
            try:
                current_user: Usuario = get_current_user_from_token(param, db)
            except HTTPException:
                print("Error al cargar el usuario, sera enviado al LOGIN")
                return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
            if (
                current_user.rol_usuario == "Administrador"
                or current_user.rol_usuario == "SuperAdmin"
            ):
              motivos = list_motivos(db=db)
              no_existe = True
              print("motivo de form")
              print(form.nombre_motivo)
              for motivo in motivos:
                  if motivo.nombre_motivo.lower() == form.nombre_motivo.lower():
                      no_existe = False
              if no_existe:
                tipo_motivo = TipoMotivoCreate(**form.__dict__)
                tipo_motivo = create_tipo_motivo(tipo_motivo=tipo_motivo, db=db)
                username = current_user.nombre_usuario
                accion = "El usuario creó un nuevo tipo de motivo: " + form.nombre_motivo
                tipo = "Gestionar tipo de motivo"
                log = create_new_registro (db, username, accion, tipo)
                print("Devuelve reespuesta correcta")
                return response
                print("Devuelve reespuesta correcta")
              else:
                print("Entra al else")
                error_nombre_motivo = "El motivo ya existe"
                tipo_motivo = ""
                return templates.TemplateResponse("admin/motivos/crear_motivos.html",
                                                  {"request": request, "tipo_motivo": tipo_motivo,
                                                   "error_nombre_motivo": error_nombre_motivo},)
            else:
                return responses.RedirectResponse(
                    "/login", status_code=status.HTTP_302_FOUND
                )
        except HTTPException:
            print("Entra al segundo 302")
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
 except requests.exceptions.ConnectionError as ce:
     raise HTTPException(status_code=503,
                         detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
