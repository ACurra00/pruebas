from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.tipo_motivos import retreive_motivo
from db.repository.tipo_motivos import update_motivo_by_id, list_motivos
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
import requests

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/motivos_admin/editar-motivo/{id}")
async def edit_tipo_motivo(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        print("Entra al endpoint")
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        print("Coge el token")
        tipo_motivo = retreive_motivo(id=id, db=db)
        response = templates.TemplateResponse(
            "admin/motivos/crear_motivos.html",
            {"request": request, "tipo_motivo": tipo_motivo},
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
            print("Es admin")
            return response
            print("No devolvio bien")
        else:
          print("No es admin")
          return responses.RedirectResponse(
            "/login", status_code=status.HTTP_302_FOUND
           )
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503,
                            detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        #print(e)
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)


@router.post("/motivos_admin/editar-motivo/{id}")
async def edit_tipo_motivo(id: int, request: Request, db: Session = Depends(get_db)):
  try:
    form = CrearMotivoForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            response = responses.RedirectResponse(
                f"/motivos_admin", status_code=status.HTTP_302_FOUND
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
              motivos = list_motivos(db=db)
              no_existe = True
              i = 0
              for motivo in motivos:
                    print(i)
                    print(motivo.nombre_motivo, form.nombre_motivo)
                    if motivo.nombre_motivo.lower() == form.nombre_motivo.lower():
                        no_existe = False
                    i = i +1
              if no_existe:
                print("No existe")
                tipo_motivo = TipoMotivoCreate(**form.__dict__)
                update_motivo_by_id(id=id, tipo_motivo=tipo_motivo, db=db)
                username = current_user.nombre_usuario
                accion = "El usuario editó un tipo de motivo"
                tipo = "Gestionar tipo de motivo"
                log = create_new_registro (db, username, accion, tipo)
                return response
              else:
                  print("Existe")
                  error_nombre_motivo = "El motivo ya existe"
                  tipo_motivo = ""
                  return templates.TemplateResponse("admin/motivos/crear_motivos.html",
                                                    {"request": request, "tipo_motivo": tipo_motivo,

                                                     "error_nombre_motivo": error_nombre_motivo}, )
            else:
              return responses.RedirectResponse(
                "login", status_code=status.HTTP_302_FOUND
              )
        except HTTPException:
            #print(HTTPException)
            return responses.RedirectResponse(
                "login", status_code=status.HTTP_302_FOUND
            )
  except requests.exceptions.ConnectionError as ce:
      raise HTTPException(status_code=503,
                          detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
