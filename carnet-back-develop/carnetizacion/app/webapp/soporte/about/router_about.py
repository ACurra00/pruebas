from typing import List
import requests
import barcode
import qrcode
from api.endpoints.router_login import get_current_user_from_token
from core.config import settings
from db.models.usuario import Usuario
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
from webapp.crear_carnet.form import crearCarnetForm
from webapp.resultado_busqueda.form_list import ListaPersonaForm

# from requests import *

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter

router = APIRouter()


@router.get("/acerca_de")
async def About(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        response = templates.TemplateResponse(
                "general_pages/soport/about.html", {"request": request})
        current_user: Usuario = get_current_user_from_token(param, db)
        if (current_user.rol_usuario == "Carnetizador" or current_user.rol_usuario == "SuperAdmin" or current_user.rol_usuario == "Administrador"):
            return response
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        #print(e)
        t =2
    #     return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
    # return templates.TemplateResponse(
    #     "general_pages/soport/about.html", {"request": request}
    # )
    # try:
    #     token = request.cookies.get("access_token")
    #     scheme, param = get_authorization_scheme_param(token)
    #     #print(token)
    #     #print(scheme)
    #     #print(users)
    #     response = templates.TemplateResponse(
    #             "general_pages/resultado_busqueda.html", {"request": request, "users": users})
    #     user_response = get_current_user_from_token(response=response,request=request,token=param, db=db)
    #     usuario_actual: Usuario = user_response["user"]
    #     #print("El usuario actual es", usuario_actual)
    #     if (
    #         usuario_actual.rol_usuario == "Carnetizador"
    #         or usuario_actual.rol_usuario == "SuperAdmin"
    #     ):
    #         return user_response["response"]
    # except Exception as e:
    #     #print(e)
    #     return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)

