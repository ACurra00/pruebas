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
from db.repository.person import list_personas_por_nombre
from db.repository.person import list_personas_por_ci
from db.repository.person import list_personas_por_nombre
from schemas.carnet_eliminado import CarnetEliminadoCreate
from db.repository.carnet_eliminado import create_new_carnet_eliminado
from db.repository.person import  retreive_person,list_personas_por_area_tipo
from db.repository.carnet_activo import lista_carnet_activo_x_ci,lista_carnet_activo_x_nombre
from db.repository.carnet_activo import cambiar_estado_por_cantidad, lista_carnet_tipo
from db.repository.carnet_activo import cambiar_estado,get_carnet_by_person, delete_carnet_activo,lista_hechos_tipo
from db.repository.carnet_con_errores import create_new_carnet_con_errores
from schemas.carnet_con_errores import CreateCarnet_con_errores
import requests
from datetime import datetime
import json
from sqlalchemy.orm import Session

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/carnets/administrar")
async def carnets_administrar(request: Request, db: Session = Depends(get_db), filtro1: str = None, filtro3: str = None,filtro4: str = None,filtro5: str = None, estado : str =None, carnet_id: str = None, error : str =None, area :str =None,rol : str = None):
    #print("estoy en carnet administrar")
    #print(area,rol,estado)
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        lista_areas, count= listaAreas(buscarAreas())
        total_areas= count
        carnets=[]
        persons = []
        if (estado != None and carnet_id != None  and filtro1 == None and filtro3 == None):
            print("Entro al cambiar uno")
            print("Estado", estado)
            print("Carnet_id", carnet_id)
            carnet_temp = str(carnet_id)
            username = current_user.nombre_usuario
            accion = "El usuario cambió de estado el carnet " + carnet_id + " a " + str(estado)
            tipo = "Cambiar estado de carnet"
            log = create_new_registro(db, username, accion, tipo)
            if(estado== "Solicitado"):
                cambiar_estado(db=db,estado=estado,ci_carnet=carnet_temp)
            elif(estado== "Hecho"):
                cambiar_estado(db=db,estado=estado,ci_carnet=carnet_temp)
            elif(estado== "Entregado"):
                cambiar_estado(db=db,estado=estado,ci_carnet=carnet_temp)
            elif(estado== "Eliminado"):
                carnet_anterior= get_carnet_by_person(carnet_temp,db)
                person=retreive_person(carnet_temp,db)
                data_carnet = dict(
                        folio_desactivo = carnet_anterior.folio,
                        area_anterior= person.area,
                        rol_anterior=person.rol,
                        )   
                carnet_eliminado = CarnetEliminadoCreate(**data_carnet)
                carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=carnet_temp)
                delete_carnet_activo(db=db,ci_carnet=carnet_temp)
                return responses.RedirectResponse("/carnets/eliminados", status_code=status.HTTP_302_FOUND)
                
            elif(estado== "Con Errores"):
                carnet_anterior= get_carnet_by_person(carnet_temp,db)
                person=retreive_person(carnet_temp,db)
                error_temp =""
                if error != None and len(error)> 0:
                    error_temp = error
                else:
                    error_temp= " no se especifico"

                data_person_con_error = dict(
                        persona_ci= carnet_temp,
                        area_con_error = person.area,
                        error = error_temp,
                        fecha_error = datetime.now(),
                        nombre_con_error= person.nombre,
                        error_simple= "Seleccionado por el carnetizador",
                    )       
                carnet_con_errores = CreateCarnet_con_errores(**data_person_con_error)

                carnet_con_errores = create_new_carnet_con_errores(carnet_con_error=carnet_con_errores, db=db)
                delete_carnet_activo(db=db, ci_carnet=carnet_temp)
                return responses.RedirectResponse("/carnets/errores", status_code=status.HTTP_302_FOUND)
            carnets = lista_carnet_activo_x_ci(db=db,carnet_ci= carnet_temp)
            persons = list_personas_por_ci(db=db, ci= carnet_temp)
        elif (estado != None and carnet_id == None  and filtro1 == None and filtro3 == None and area != None and rol != None ):
            area_temp = str(area)
            rol_temp = str(rol)
            print(area_temp)
            print(rol_temp)
            username = current_user.nombre_usuario
            accion = "El usuario cambió por lotes los estados de los carnets del área " + area_temp + " del rol " + rol_temp + " a " + str(estado)
            tipo = "Cambiar estado de carnet"
            log = create_new_registro(db, username, accion, tipo)
            if(estado== "Solicitado"):  
                cambiar_estado_por_cantidad(db=db,estado=estado,area = area_temp, rol= rol_temp)
            elif(estado== "Hecho"):
                cambiar_estado_por_cantidad(db=db,estado=estado,area = area_temp, rol= rol_temp)
            elif(estado== "Entregado"):
                cambiar_estado_por_cantidad(db=db,estado=estado,area = area_temp, rol= rol_temp)
            elif(estado== "Eliminado"):
                #print("no se ha implementado para eliminado")
                d = 2
            elif(estado== "Con Errores"):
                #print("no se ha implementado para con errores")
                c = 1
            print("Termina de cambiar el estado bien")
            carnets = lista_carnet_tipo(db=db,tipo= rol_temp,area=area_temp,estado= estado)
            persons = list_personas_por_area_tipo(db=db,area=area,tipo=rol_temp)
            print("TOma carnets y personas bien")
        if(filtro1 != None and len(filtro1)==11  and filtro1 !=""):# filtro para el buscar solo por el carnet
            print("estpu aqui")
            carnets = lista_carnet_activo_x_ci(db=db,carnet_ci= filtro1)
            persons = list_personas_por_ci(db=db, ci= filtro1)
        elif(filtro3 != None and filtro3 != ""):
            #print("estoy aquiaaaa")
            carnets = lista_carnet_activo_x_nombre (db=db, nombre=filtro3)# filtro solo para buscar por el nombre
            persons = list_personas_por_nombre(db=db, nombre=filtro3) 
        elif(filtro4!= None and filtro4!=""):
            print("El area es")
            print(filtro4)
            print("El filtro es:")
            print(filtro5)
            if(filtro5 =="change_Becado"):
                carnets = lista_hechos_tipo(db=db,tipo= "Becado Nacional",area=filtro4)
                persons = list_personas_por_area_tipo(db=db,area=filtro4,tipo="Becado Nacional")
            if(filtro5 =="change_Seminterno"):
                carnets = lista_hechos_tipo(db=db,tipo= "Seminterno",area=filtro4)
                persons = list_personas_por_area_tipo(db=db,area=filtro4,tipo="Seminterno")
            if(filtro5 =="change_Externo"):
                carnets = lista_hechos_tipo(db=db,tipo= "Externo",area=filtro4)
                persons = list_personas_por_area_tipo(db=db,area=filtro4,tipo="Externo")
            elif(filtro5 =="change_Docente"):
                carnets = lista_hechos_tipo(db=db,tipo= "Docente",area=filtro4)
                persons = list_personas_por_area_tipo(db=db,area=filtro4,tipo="Docente")
            elif(filtro5 =="change_No_Docente"):
                carnets = lista_hechos_tipo(db=db,tipo= "No Docente",area=filtro4)
                persons = list_personas_por_area_tipo(db=db,area=filtro4,tipo="No Docente")

        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)

        if filtro1 is not None or filtro3 is not None or filtro4 is not None or filtro5 is not None:
         if carnets != []:
          if carnets.count() == 0:
            error_nada = "No hay resultados para los campos especificados"
            return templates.TemplateResponse(
              "general_pages/carnets/carnets_administrar.html", {"request": request,
               "carnets": carnets,
               "lista_areas" :lista_areas,
              "total_areas": total_areas,
              "persons": persons,
                "error_nada" : error_nada
              }
             )
        response = templates.TemplateResponse(
            "general_pages/carnets/carnets_administrar.html", {"request": request,
            "carnets": carnets,
            "lista_areas" :lista_areas,
            "total_areas": total_areas, 
            "persons": persons
            }
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
    except HTTPException:
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        print(e)
        #print("Error en carnet administrar")
        raise Exception("Error provocado por el desarrollador ", e)
    
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