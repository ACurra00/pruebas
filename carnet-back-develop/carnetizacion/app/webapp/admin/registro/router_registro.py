from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.usuario import lista_usuarios
from db.session import get_db
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from pytest import Session
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from db.repository.registro import lista_registro

from db.repository.registro import lista_filtrados_por_usuario

from db.repository.registro import lista_filtrados_por_tipo

from db.repository.registro import lista_filtrados_por_fecha

from db.repository.registro import lista_filtrados_por_fecha_rango, lista_registros_filtrado_por_todos

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/registro_admin")
async def registro(request: Request, page: int = 1,filtro1: str = None,filtro2: str = None,filtro3: str = None,filtro4: str = None, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
        current_user: Usuario = get_current_user_from_token(param, db)
        registros_usuario = lista_registros_filtrado_por_todos(db=db, username=filtro1, fecha_inicio=filtro2, fecha_fin=filtro3, tipo=filtro4)
        #lista = lista_registro(db=db)

        paginator = Paginator(registros_usuario, 20)

        page_number = page

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_number = 1
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        numero = page_obj.previous_page_number
        response = templates.TemplateResponse(
            "admin/registro/admin_registro.html",
            {"request": request, "lista_registro": registros_usuario,
             'page_obj': page_obj,
             'page': page_number}
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
        #print("El Usuario no es Administrador")
        raise Exception("Error provocado por el desarrollador  " ,e)