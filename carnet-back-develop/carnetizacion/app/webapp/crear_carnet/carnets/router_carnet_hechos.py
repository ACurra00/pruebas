import json
import requests

from api.endpoints.router_login import get_current_user_from_token
from api.endpoints.router_login import refreshToken
from core.config import settings
from db.models.usuario import Usuario
from db.session import get_db
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from db.repository.carnet_activo import lista_hechos
from db.repository.carnet_activo import lista_hechos_filtrado_por_todos
from db.repository.person import list_persons
from db.repository.person import list_personas_por_todos
from db.repository.tipo_motivos import list_motivos
from sqlalchemy.orm import Session

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

@router.get("/carnets/hechos")
async def carnet_hechos(request: Request, db: Session = Depends(get_db),page: int = 1,filtro1: str = None,filtro2: str = None, filtro3: str = None):
    #print("estoy en carnet Hechos")
    #print("1er filtro", filtro1)
    #print("2do filtro", filtro2)
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        
        carnets = lista_hechos_filtrado_por_todos(db=db, carnet_ci=filtro1, area=filtro2, nombre=filtro3)
        persons = list_personas_por_todos(db=db, ci=filtro1, area=filtro2, nombre=filtro3) 
        motivos = list_motivos(db=db)
        
       
        paginator = Paginator(carnets, 20) # 6 employees per page
        
        page_number = page
        #print("este es el numero de la pagina ")
        #print(page_number)

       
       
       
       
       
        try:
            page_obj = paginator.page(page_number)
            
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_number = 1
            page_obj = paginator.page(page_number)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        
        numero =page_obj.previous_page_number
        
        if filtro1 is not None or filtro2 is not None or filtro3 is not None:
            print("Los filtros al menos algunos no son NOne")
            if carnets.count() == 0:
                print("Entra al error ")
                error_nada = "No hay coincidencias para los filtros especificados"
                return templates.TemplateResponse(
                     "general_pages/carnets/carnets_hechos.html", {"request": request,
                                                          "carnets": carnets,
                                                          "persons": persons,
                                                          "motivos":motivos,
                                                          "page_obj":page_obj,
                                                          "page": page_number,
                                                          "error_nada": error_nada})
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_hechos.html", {"request": request,
                                                          "carnets": carnets,
                                                          "persons": persons,
                                                          "motivos":motivos,
                                                          "page_obj":page_obj,
                                                          "page": page_number}
        )
        try:
            current_user: Usuario = get_current_user_from_token(param, db)
        except HTTPException:
            #print("Error al cargar el usuario, sera enviado al LOGIN")
            return  responses.RedirectResponse("login", status_code=status.HTTP_401_UNAUTHORIZED)
        if (
            current_user.rol_usuario == "Carnetizador"
            or current_user.rol_usuario == "SuperAdmin"
            or current_user.rol_usuario == "Administrador"
        ):
            return response
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        #print(e)
        #print("Error carnet hecho")
        raise Exception("Error provocado por el desarrollador  ",e)
