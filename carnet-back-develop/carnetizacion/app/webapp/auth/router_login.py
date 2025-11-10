from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import login_for_access_token
from db.repository.login import get_user
from db.session import get_db
from fastapi import APIRouter
from db.repository.usuario import update_state_usuario_by_id_logout
from api.endpoints.router_login import get_current_user_from_token
from fastapi.security.utils import get_authorization_scheme_param
from db.models import usuario
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from webapp.auth.forms import LoginForm

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

router = APIRouter()
userGeneral = None

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login")
def login(request: Request):
    print("Muestra el login")
    return templates.TemplateResponse("login/login.html", {"request": request})
    #return templates.TemplateResponse("templates_visitantes/pages/home.html", {"request": request})

@router.get("/portal")
def portal(request: Request):
    print("Muestra el portal")
    return templates.TemplateResponse("portal.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    print("Se autentico")
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
            response = templates.TemplateResponse("login/login.html", form.__dict__)
            user = get_user(nombre_usuario=form.username, db=db)

            if user is None:
                ##print("Usuario no encontrado")
                form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
                form.__dict__.update(msg="")
                return templates.TemplateResponse("login/login.html", form.__dict__)

            form.__dict__.update(msg="Inicio de Sesion Exitoso :)")
            print("EL rol del usuarios es: ")
            print(user.rol_usuario)
            if user.rol_usuario == "Carnetizador":
                ##print("entro carnetizador")
                userGeneral = user
                response = responses.RedirectResponse(
                     f"/", status_code=status.HTTP_302_FOUND)
            elif (
                    user.rol_usuario == "Administrador" or user.rol_usuario == "SuperAdmin"):

                response = RedirectResponse(
                    f"/admin", status_code=status.HTTP_302_FOUND
                )
                
            elif (user.rol_usuario == "Recepcionista"):
                response = RedirectResponse(f"/recepcionista", status_code=status.HTTP_302_FOUND)
            try:
                login_a = login_for_access_token(response, form, db)
            except Exception:
                ##print("Usuario o Contraseña from LDAP")
                form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
                form.__dict__.update(msg="")
                return templates.TemplateResponse("login/login.html", form.__dict__)

            authorization: str = login_a["access_token"]  # changed to accept access token from httpOnly Cookie
            username = user.nombre_usuario
            accion = "El usuario se autenticó"
            tipo = "Autenticarse"
            log = create_new_registro(db, username, accion, tipo)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")

    else:
        ##print("error de autentificacion")
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append("Incorrecto Usuario o Contraseña")
        return templates.TemplateResponse("login/login.html", form.__dict__)


@router.get("/cerrarsesion")
def logout(request: Request, db: Session = Depends(get_db)):
    print("Voy a cerrar sesion")
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token)  # scheme will hold "Bearer" and param will hold actual token value

        response = responses.RedirectResponse(
            "/login", status_code=status.HTTP_302_FOUND
        )
        try:
            current_user: usuario = get_current_user_from_token(param, db)
        except HTTPException:
            ##print("No se encontro el usuario")
            response = responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="access_token", value="", httponly=True)
            response.set_cookie(key="refresh_token", value="", httponly=True)
            return response

        ##print("El usuario actual es: ", current_user.nombre_usuario)

        update_state_usuario_by_id_logout(current_user.id, db)
        ##print("------> cession cerrada <-----")

        response.set_cookie(key="access_token", value="", httponly=True)
        response.set_cookie(key="refresh_token", value="", httponly=True)
        return response
    except Exception as e:
        ##print(e)
        b = 0 + 1
