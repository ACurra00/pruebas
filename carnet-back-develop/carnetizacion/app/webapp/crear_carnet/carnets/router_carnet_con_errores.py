from operator import imod
from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.session import get_db
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.params import Depends
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from db.repository.carnet_con_errores import lista_carnet_con_errores
from db.repository.carnet_con_errores import lista_con_errores_filtrado_por_ci
from db.repository.carnet_con_errores import lista_con_errores_filtrado_por_area
from db.repository.person import list_personas_por_ci, list_personas_por_area
from db.repository.person import list_personas_por_nombre
from db.repository.person import list_personas_por_todos
from db.repository.carnet_con_errores import lista_con_errores_filtrado_por_nombre
from db.repository.carnet_con_errores import lista_con_errores_filtrado_por_todos
from db.repository.person import list_persons
import json
from sqlalchemy.orm import Session
import xlwt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import pandas as pd
from io import BytesIO # Add to Top of File
from fastapi.responses import StreamingResponse
import requests

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()

def export_excel(export: str,list):
    df = pd.DataFrame(columns=['persona_ci','area_con_error', 'error', 'fecha_error','nombre_con_error','error_simple'])
    for temp in list:
        df = df.append(pd.Series([temp.persona_ci, temp.area_con_error, temp.error,temp.fecha_error,temp.nombre_con_error, temp.error_simple], index=['persona_ci','area_con_error', 'error', 'fecha_error','nombre_con_error','error_simple']), ignore_index=True)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)
    
    return StreamingResponse(
        BytesIO(buffer.getvalue()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename=data.csv"}
)
    

@router.get("/carnets/errores")
async def carnet_con_errores(request: Request, db: Session = Depends(get_db),page: int = 1, filtro1: str = None,filtro2: str = None,filtro3: str = None, export : str =None):
    #print("estoy en carnet con errores")
    try:
        
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        lista_areas, count= listaAreas(buscarAreas())
        total_areas= count
        if(export != None and len(export)>2 and export !=""): #exportar carnet
            #print("estoy aqui")
            carnets = lista_con_errores_filtrado_por_area(db=db,area=export)
            #print("1")
            
            return export_excel(export=export, list= carnets)

        #if(filtro1 != None and len(filtro1)==11  and filtro1 !=""):# filtro para el buscar solo por el carnet
        #    carnets = lista_con_errores_filtrado_por_ci(db=db,carnet_ci= filtro1)
        #    persons = list_personas_por_ci(db=db, ci= filtro1)
        #elif(filtro2 != None and filtro2 != ""): # filtro para las areas
        #    carnets = lista_con_errores_filtrado_por_area(db=db,area=filtro2)
        #    persons = list_personas_por_area(db=db, area= filtro2)
        #elif(filtro3 != None and filtro3 != ""):
        #    carnets = lista_con_errores_filtrado_por_nombre(db=db, nombre=filtro3)
        #    persons = list_personas_por_nombre(db=db, nombre=filtro3)
        #else: # filtro para todos
        #    carnets = lista_carnet_con_errores(db=db)

        print("Los filtros:")
        print(filtro1)
        print(filtro2)
        print(filtro3)
        carnets = lista_con_errores_filtrado_por_todos(db=db, carnet_ci=filtro1, area=filtro2, nombre=filtro3)
        persons = list_personas_por_todos(db=db, ci=filtro1, area=filtro2, nombre=filtro3)
        #persons = list_persons(db=db)     
        

        paginator = Paginator(carnets, 20) # 6 employees per page
        
        
        
        page_number = page
       
        try:
            page_obj = paginator.page(page_number)
            
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_number= 1
            page_obj = paginator.page(page_number)
           
            
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)


        print("Total :")
        print(carnets.count())
        numero =page_obj.previous_page_number
        if filtro1 is not None or filtro2 is not None or filtro3 is not None:
            print("Los filtros al menos algunos no son NOne")
            if carnets.count() == 0:
                print("Entra al error ")
                error_nada = "No hay coincidencias para los filtros especificados"
                return templates.TemplateResponse(
                     "general_pages/carnets/carnets_con_errores.html", {"request": request,
                                                          "carnets": carnets,
                                                          "persons": persons,
                                                          "page_obj":page_obj,
                                                          "page": page_number,
                                                          "error_nada": error_nada})
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_con_errores.html", {"request": request,
            "total_areas": total_areas,
            "lista_areas":lista_areas,
            "carnets": carnets,
            'page_obj': page_obj,
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
        #print("Error en carnet con errores")
        raise Exception("Error provocado por el desarrollador  ",e)
    
def listaAreas(text : str):
    result = json.loads(str(text))          
    lista=""
    count =0
    for iter in result:
        iter['name']
        count= count +1
        lista= lista +iter['name']+ ","
    
    return lista, count

def buscarAreas():
    import requests

    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/areas"

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=" 
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
    
    return response.text