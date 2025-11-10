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
from db.repository.carnet_eliminado import lista_eliminados
from db.repository.carnet_eliminado import eliminar_eliminados
from db.repository.carnet_eliminado import lista_eliminados_array
from db.repository.carnet_eliminado import lista_eliminados_filtrado_por_ci
from db.repository.carnet_eliminado import lista_eliminados_filtrado_por_area
from db.repository.person import list_personas_por_ci, list_personas_por_area
from db.repository.person import list_personas_por_nombre
from db.repository.carnet_eliminado import lista_eliminados_filtrado_por_nombre
from db.repository.carnet_eliminado import lista_eliminados_filtrado_por_todos
from db.repository.person import list_persons
from db.repository.person import list_personas_por_todos
from db.repository.tipo_motivos import list_motivos
from sqlalchemy.orm import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

@router.get("/carnets/eliminados")
async def carnet_eliminado(request: Request, db: Session = Depends(get_db),page: int = 1,filtro1: str = None,filtro2: str = None,filtro3: str = None):
    #print("estoy en carnet Eliminados")
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)

        
        '''if(filtro1 != None and len(filtro1)==11  and filtro1 !=""):# filtro para el buscar solo por el carnet
            carnets = lista_eliminados_filtrado_por_ci(db=db,carnet_ci= filtro1)
            persons = list_personas_por_ci(db=db, ci= filtro1)
        elif(filtro2 != None and filtro2 != ""): # filtro para las areas
            carnets = lista_eliminados_filtrado_por_area(db=db,area=filtro2)
            persons = list_personas_por_area(db=db, area= filtro2)
        elif(filtro3 != None and filtro3 != ""):
            carnets = lista_eliminados_filtrado_por_nombre(db=db, nombre=filtro3)
            persons = list_personas_por_nombre(db=db, nombre=filtro3)
        else: # filtro para todos
            carnets = lista_eliminados(db=db)
            persons = list_persons(db=db)  
        '''    
        carnets = lista_eliminados_filtrado_por_todos(db=db, carnet_ci=filtro1, area=filtro2, nombre=filtro3)

        #aux = lista_eliminados_array(db=db)
        #if len(aux) > 10:
            #eliminar_eliminados(db=db)

        persons = list_personas_por_todos(db=db, ci=filtro1, area=filtro2, nombre=filtro3)      
        
        motivos = list_motivos(db=db)
         
        paginator = Paginator(carnets, 20) # 6 employees per page
        
        
        
        page_number = page
        

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(page_number)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        if filtro1 is not None or filtro2 is not None or filtro3 is not None:
            print("Los filtros al menos algunos no son NOne")
            if carnets.count() == 0:
                print("Entra al error ")
                error_nada = "No hay coincidencias para los filtros especificados"
                return templates.TemplateResponse(
                     "general_pages/carnets/carnets_eliminados.html", {"request": request,
                                                          "carnets": carnets,
                                                          "persons": persons,
                                                          "motivos":motivos,
                                                          "page_obj":page_obj,
                                                          "page": page_number,
                                                          "error_nada": error_nada})
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_eliminados.html", {"request": request, 
                                                              "carnets": carnets,
                                                              "persons": persons,
                                                              "motivos":motivos,
                                                              "page_obj": page_obj,
                                                              'page': page_number}
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
        #print("Error carnet eliminado")
        raise Exception("Error provocado por el desarrollador  " +e)
