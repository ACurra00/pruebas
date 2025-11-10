import html

from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import create_new_user, lista_usuarios
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
import json
import requests

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

router = APIRouter()

#Para validar que exista en el ldap
def buscarTrabajdor_and_Estudiante(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/search-all"

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "identification": ci,
        "name": "",
        "lastname": "",
        "surname": "",
        "email": "",
        "area": ""
    })

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    result = json.loads(str(response.text))
    if (bool(result)):
        return result
    else:
        return None

@router.get("/usuario_admin/form_usuario")
async def form_usuarios(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        usuario = ""
        response = templates.TemplateResponse(
            "admin/usuarios/crear_usuario.html",
            {"request": request, "usuario": usuario},
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
    except HTTPException:
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503,
                            detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        #print(e)
        #print("Error en Form Usuarios")
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)


@router.post("/usuario_admin/form_usuario")
async def form_usuarios(request: Request, db: Session = Depends(get_db)):
  try:
    print("Router form usuarios post")
    form = CrearUsuarioForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            
            response = responses.RedirectResponse(
                f"/usuario_admin", status_code=status.HTTP_302_FOUND
            )
            try:
                current_user: Usuario = get_current_user_from_token(param, db)
            except HTTPException:
                print("Error al cargar el usuario, sera enviado al LOGIN")
                return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
            aux = buscarTrabajdor_and_Estudiante(form.nombre_usuario)
            if aux is not None:
             aux1 = aux[0]
             form.nombre_usuario = html.escape(aux1['user'])
             print("El nombre usuario sacado de ldap es: ")
             print(aux1['user'])
             print("El nombre usuario sacado ahora en el form es: ")
             print(form.nombre_usuario)
             if (
                current_user.rol_usuario == "Administrador"
                or current_user.rol_usuario == "SuperAdmin"
             ):
              usuarios = lista_usuarios(db=db)
              no_existe = True
              print("Usuarios :")
              for actual in usuarios:
                  print(actual.nombre_usuario)
                  if actual.nombre_usuario == form.nombre_usuario:
                      no_existe= False
              if no_existe:
                usuario = UsuarioCreate(**form.__dict__)
                print("usuario antes de llamar al crud pero luego de usuarioCreate con el form")
                print(usuario.nombre_usuario)
                usuario = create_new_user(user=usuario, db=db)
                print("usuario luego de llamar al crud")
                print(usuario.nombre_usuario)
                username = current_user.nombre_usuario
                accion = "El usuario creó un usuario: " + usuario.nombre_usuario
                tipo = "Gestionar usuarios"
                log = create_new_registro(db, username, accion, tipo)
                return response
              else:
                  error_nombre_usuario = "El usuario ya existe"
                  usuario = ""
                  return templates.TemplateResponse(
                      "admin/usuarios/crear_usuario.html",
                      {"request": request, "usuario": usuario, "error_nombre_usuario": error_nombre_usuario},
                  )
             else:
                 return responses.RedirectResponse(
                     "/login", status_code=status.HTTP_302_FOUND
                 )
            else:
                usuario = ""
                error_usuario_inexistente = "El usuario no existe en el ldap"
                return templates.TemplateResponse(
                    "admin/usuarios/crear_usuario.html",
                    {"request": request, "usuario": usuario,
                     "error_usuario_inexistente": error_usuario_inexistente},
                )
        except HTTPException:
            #print(HTTPException)
            return responses.RedirectResponse(
                "/login", status_code=status.HTTP_302_FOUND
            )
  except requests.exceptions.ConnectionError as ce:
      raise HTTPException(status_code=503,
                          detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
