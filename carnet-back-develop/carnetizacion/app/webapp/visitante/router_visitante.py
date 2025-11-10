import jwt
from api.endpoints.router_login import get_current_user_from_token
from db.repository.usuario import update_state_usuario_by_id_logout
from db.models.usuario import Usuario
from db.session import get_db
from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi import responses

from fastapi import status
from fastapi.params import Depends
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.config import settings
import requests
import json

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/recepcionista")
async def recepcionista(request: Request,
                        db: Session = Depends(get_db),
                        ):
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(
        token)  # scheme will hold "Bearer" and param will hold actual token value
    count = repr(cantidad_trabajadores_and_estudiantes())
    response = templates.TemplateResponse(
        "templates_visitantes/pages/home.html", {"request": request, "count": count})
    try:
        current_user: Usuario = get_current_user_from_token(param, db)
    except HTTPException:
        #print("Error al cargar el usuario, sera enviado al LOGIN")
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)

    if (current_user.rol_usuario == "Recepcionista"):
        #print("Recepecion - > User: " + current_user.nombre_usuario)
        return response
    #print("El usuario actual no es de la recepcion -> Login")
    return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)


def cantidad_trabajadores_and_estudiantes():
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/persons?area=OU=DG de ICI,OU=Area Central,DC=cujae,DC=edu,DC=cu"
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA="
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload, headers=headersList)

    responseArray = response.json()
    count = len(responseArray)
    #print("cantidad total de trabajadores ", count)
    return count
