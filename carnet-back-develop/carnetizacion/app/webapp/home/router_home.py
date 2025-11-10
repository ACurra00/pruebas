import json
import requests
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
from sqlalchemy.orm import Session
from webapp.home.form import BuscarPersonaForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from db.repository.person import create_new_person, retreive_person,update_person_by_ci
from db.repository.carnet_activo import get_carnet_by_person
from db.repository.carnet_activo import update_carnetactivo_by_ci
from db.session import get_db_roles
from db.repository.roles_db import get_trabajador_con_cargo
from schemas.person import PersonCreate
from schemas.carnet_eliminado import CarnetEliminadoCreate
from db.repository.carnet_eliminado import create_new_carnet_eliminado
import datetime
from db.repository.carnet_activo import create_new_carnet_activo
from schemas.carnet_activo import CarnetActivoCreate
from db.repository.carnet_con_errores import create_new_carnet_con_errores
from schemas.carnet_con_errores import CreateCarnet_con_errores
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import HTMLResponse

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")
from typing import Optional
# from api.endpoints.web.user import router as userRouter


router = APIRouter()



@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), page:int= 1, area2: str = None):
    ###print("aqiui estopy")
    try:
        ###print(page, area2)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        is_x_lotes = False
        lista_areas, count= listaAreas(buscarAreas())
        print("Lista areas")
        print(listaAreas(buscarAreas()))
        total_areas= count
        listResult = []
        page_number =1
        if (page > 0 and area2 != "" and area2 is not None):
            ###print("esto aqui en el paginado")
            is_x_lotes = True
            areatemp=buscarAreas_por_name(buscarAreas(),area2)
            listResult = carnet_x_lote(areatemp)
            print("Carnet x lote")
            print(carnet_x_lote(areatemp))
            page_number = page
        else:        
            listResult = []
        
        paginator = Paginator(listResult, 20) # 6 employees per page

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        
        response = templates.TemplateResponse(
            "general_pages/homepage.html", {"request": request, 'area': area2, "total_areas": total_areas, "lista_areas":lista_areas,
            "page_obj": page_obj,"is_x_lotes": is_x_lotes})
        
        try:
            current_user: Usuario = get_current_user_from_token(param, db)
        except HTTPException:
            ###print("Error al cargar el usuario, sera enviado al LOGIN--")
            return templates.TemplateResponse("/portal.html", {"request": request})
            response = templates.TemplateResponse(
                "/portal.html", {"request": request})
       
            return response
        if (
            current_user.rol_usuario == "Carnetizador"
            or current_user.rol_usuario == "SuperAdmin"
            or current_user.rol_usuario == "Administrador"
        ):
            return response
    except Exception as e:
        ###print(e)
        ###print("Error Home")
        raise Exception("Error provocado por el desarrollador  ",e)
    except requests.exceptions.ConnectionError as ce:
        print("Se perdio la conexion")
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

def listaAreas(text : str):
    result = json.loads(str(text))          
    lista=""
    count =0
    for iter in result:
        iter['name']
        count= count +1
        lista= lista +iter['name']+ ","
    
    return lista, count

def buscarAreas_por_name(text: str, areaID):
    result = json.loads(str(text))
    area = ""
    for iter in result:
        if iter['name'] == areaID:
            area = iter['distinguishedName']
            break

    return area
def buscar_personas_por_areas(area: str):
    
        reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/persons?area="+area

        headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
            "Content-Type": "application/json" 
            }

        payload = json.dumps({
        "area":area
        })

        response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
        users =  json.loads(str(response.text))
        return users
        
def buscarTrabajdor_and_Estudiante(ci: str,area: str):

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
    "area": area
    })

    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    
    result = json.loads(str(response.text))
    if(bool(result)):
        return result
    else:
        ###print("no se encontro el Usuario en esa area")
        return None




def buscarAreas():
    #import requests

    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/areas"

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=" 
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
    
    return response.text
    
def carnet_para_Persona(area: str, ci: str):
    if  area != "":
        ###print("Area Encontrada")
        usuario  = buscarTrabajdor_and_Estudiante(ci,area)               
        if usuario is not None:
            return [usuario[0]]
        else:
            ###print("No se encontro el usuario")
            c = 1+0
       
def carnet_x_lote(area: str, tipo:str, year: str):
    userstemp = buscar_personas_por_areas(area)
    listResult = []
    for temp in userstemp:
        try:
            tipoPersona = temp['personType']
        except Exception:
            tipoPersona =""
        try:        
            tipoProfesor = temp ['personTeacher']
        except Exception:
            tipoProfesor = "FALSE"
        try:
            tipoyear = temp ['studentYear']
        except Exception:
            tipoyear = ""    

        
        if tipoPersona == "Worker" and tipo == "carnet_x_lotes_Docente" and tipoProfesor == "TRUE": # Docente
            listResult.append(temp)
        elif tipoPersona == "Worker" and tipo == "carnet_x_lotes_No_Docente": # no docente
            listResult.append(temp)
        if tipoPersona =="Student" and tipo == "carnet_x_lotes_Estudiante":
            if year == "carnet_x_lotes_one" and tipoyear == "1":
                listResult.append(temp)
            if year == "carnet_x_lotes_two" and tipoyear == "2":
                listResult.append(temp)
            if year == "carnet_x_lotes_three" and tipoyear == "3":
                listResult.append(temp)
            if year == "carnet_x_lotes_four" and tipoyear == "4":
                listResult.append(temp)
            if year == "carnet_x_lotes_five" and tipoyear == "5":
                listResult.append(temp)            

        
    return listResult

@router.post("/")
async def home(request: Request, db: Session = Depends(get_db), page: int=1):
  try:
    print("Entra al buscar")
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    form = BuscarPersonaForm(request)
    lista_areas, count= listaAreas(buscarAreas())
    total_areas= count
    is_x_lotes = False
    listResult = []
    await form.load_data()
    value = form.is_valid()
    if value:
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            
            area = buscarAreas_por_name(buscarAreas(),form.areaBuscarPersona)
            ###print("area",area)
            ###print ("Procesando la busqueda de persona")
            ###print("La  busqueda es: ", form.tipoBuscarPersona)
            ci = form.ciBuscarPersona
            
            
            if (form.tipoBuscarPersona == "carnet_x_lotes_off"):
                is_x_lotes = False
               
                users = carnet_para_Persona(area,ci)
                if not users:  # Comprueba si users está vacío
                    # Maneja el caso en que no se encuentren usuarios
                    page_number = page
                    paginator = Paginator(listResult, 20)
                    page_obj = paginator.page(paginator.num_pages)
                    error_no_existe = "No se encontraró a la persona en el área especificada"
                    return templates.TemplateResponse(
                        "general_pages/homepage.html",
                        {
                            'request': request,
                            'users': [],
                            'area': form.areaBuscarPersona,
                            "lista_areas": lista_areas,
                            "total_areas": total_areas, "page_obj": page_obj,
                            "error_no_existe": error_no_existe
                        })
                listResult.append(users[0])
                page_number = page
                paginator = Paginator(listResult, 20) # 20 employees per page

                try:
                    
                    page_obj = paginator.page(page)
                    
                except PageNotAnInteger:
                                        # if page is not an integer, deliver the first page
                    page_obj = paginator.page(1)
                except EmptyPage:
                         # if the page is out of range, deliver the last page
                    page_obj = paginator.page(paginator.num_pages)
                responsePersona= templates.TemplateResponse("general_pages/homepage.html",
                {'request':request, 'users':users, 'area': form.areaBuscarPersona, "lista_areas" :lista_areas,
                "total_areas": total_areas, "page_obj": page_obj, "is_x_lotes": is_x_lotes, "tipo": form.tipoBuscarCarnet, "year": form.student_year
                })
                return responsePersona
           
           
            elif (form.tipoBuscarPersona == "carnet_x_lotes_on"):
                print("Entro a por lotes on")
                is_x_lotes = True
                listResult = carnet_x_lote(area,form.tipoBuscarCarnet,form.student_year)

                print("La lista es")
                print(listResult)
    
                page_number = page
                paginator = Paginator(listResult, 20) # 20 employees per page

                try:
                    
                    page_obj = paginator.page(page_number)
                    
                except PageNotAnInteger:
                                        # if page is not an integer, deliver the first page
                    page_obj = paginator.page(1)
                except EmptyPage:
                         # if the page is out of range, deliver the last page
                    page_obj = paginator.page(paginator.num_pages)
                if listResult == []:
                    error_no_existe = "No se encontraron personas para los datos especificados"
                    return templates.TemplateResponse("general_pages/homepage.html",
                                                                          {'request': request, "page_obj": page_obj,
                                                                           'area': form.areaBuscarPersona,
                                                                           "lista_areas": lista_areas,
                                                                           "total_areas": total_areas,
                                                                           "tipo": form.tipoBuscarCarnet,
                                                                           "year": form.student_year,
                                                                           "error_no_existe": error_no_existe
                                                                           })

                responses_carnet_x_lotes= templates.TemplateResponse("general_pages/homepage.html",
                {'request':request,  "page_obj": page_obj, 'area':form.areaBuscarPersona, "lista_areas" :lista_areas,
                "total_areas": total_areas, "is_x_lotes": is_x_lotes,"tipo": form.tipoBuscarCarnet, "year": form.student_year
                })
                return responses_carnet_x_lotes

        except HTTPException as e:
            ##print("Error en Home")
            ##print (e)
            response = templates.TemplateResponse(
            "general_pages/homepage.html",
             {"request": request,
               "total_areas": total_areas,
                "lista_areas":lista_areas,
                "page_obj": page_obj,
                "is_x_lotes": is_x_lotes,
                })
            return response

    else:
        listResult =[]
        paginator = Paginator(listResult, 20)    
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        errorArea= form.errorArea
        errorCI = form.errorCI
        errorFiltro= form.errorFiltro
        erroryear = form.erroryear

        response = templates.TemplateResponse(
                "general_pages/homepage.html",
                {"request": request,
                "total_areas": total_areas,
                "lista_areas":lista_areas,
                "errorArea": errorArea,
                "page_obj": page_obj,
                "is_x_lotes": is_x_lotes,
                "errorCI": errorCI,
                "errorFiltro": errorFiltro,
                "erroryear": erroryear })
        return response
  except HTTPException:
      return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
  except requests.exceptions.ConnectionError as ce:
      raise HTTPException(status_code=503,
                          detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")

def carnet_por_lotes(area: str,tipo: str, year: str, request: Request, db: Session = Depends(get_db), dbroles: Session = Depends(get_db_roles)):
    tipo_error = "Unknown"
    error_simple= "Desconocido"
    print("ID area")
    print(area)
    print("Areas")
    print(buscarAreas())
    areatemp=  buscarAreas_por_name(buscarAreas(),area)
    print("AreaTemp")
    print(areatemp)
    print("YEAR")
    print(year)
    listResult = carnet_x_lote(areatemp,tipo,year)
    print("Lista")
    print(listResult)
    count =1
    for user in listResult:
        ci_temp = user['identification']
        try: 
            usuario= buscarTrabajdor_and_Estudiante(ci_temp,areatemp)
            
            if usuario is not None:

                person=retreive_person(ci_temp,db)
                carnet_anterior=get_carnet_by_person(ci_temp,db)

                annoEstudiantePersona= -1
                tipoPersona=""
                rol_temp =""
                comprobante_motivo = "carnets creado x Lotes"
                estado = "Solicitado"
                tipoMotivo= "Carnet x Lotes"
                folio_desactivo_temp =-1
                area_temp = area
                area_anterior_temp= ""
                rol_anterior_temp = ""
                
                try:
                    nombre_temp= user['name']+" "+user['surname']+" "+user['lastname']
                except Exception:
                            tipo_error = "Name Problem"
                            error_simple = "Problema con el nombre o apellido"
                            nombre_temp = "Uknown"
                            raise Exception("Error provocado por el desarrollador")
                
                if(user["personType"] == "Student"):
                        try:
                            rol_temp = buscar_Tipo_Estudiante_carnet(ci_temp)
                        except Exception:
                            tipo_error = "Student Type Problem"
                            error_simple = "Tipo de estudiante Desconocido"
                            raise Exception("Error provocado por el desarrollador")
                        try:
                            annoEstudiantePersona= user['studentYear']
                        except Exception:
                            tipo_error = "Student Year Problem"
                            error_simple = "Problema con el anno"
                            raise Exception("Error provocado por el desarrollador")

                        tipoPersona = "Estudiante"
                else:
                    tipoPersona = "Trabajador"
                    try:
                        if user["personTeacher"] == "TRUE":
                            rol_temp= "Docente"         
                        elif user["personTeacher"] == "FALSE":
                            rol_temp = "No Docente"
                    except Exception:
                        tipo_error = "PersonTeacher Problem"
                        error_simple = "Tipo de trabajador Desconocido"
                        raise Exception("Error provocado por el desarrollador")

                found = get_trabajador_con_cargo(ci_temp,dbroles)

                if found !="" and found is not None:
                    rol_temp = found 

                folio = None

                if carnet_anterior != None:
                    m = 1+0
                else:
                    ma = 1+0
                if person is None:
                    mb = 1+0
                else:
                    mav = 1+0
                if(user["personType"] == "Student"):
                    ms= 1+0
                if person is None:
                    mn = 1+0
                else:
                    mm = 1+0

                if person is None:
                    data_person = dict(
                        ci=ci_temp,
                        nombre=nombre_temp,
                        area=area_temp,
                        rol= rol_temp ,
                    )
                    person_a = PersonCreate(**data_person)
                    person_a = create_new_person(person_a, db)

                else:
                    folio_desactivo_temp = carnet_anterior.folio
                    area_anterior_temp = person.area
                    rol_anterior_temp = person.rol
                    data_person = dict(
                        ci=ci_temp,
                        nombre=nombre_temp,
                        area=area_temp,
                        rol= rol_temp ,
                    )   
                    person_a = PersonCreate(**data_person)
                    person_a = update_person_by_ci(ci_temp, person_a,db)

                if carnet_anterior is not None: # si tiene carnet anterior
                    ##print("existia un carnet anterior y se actualizara")
                    folio_desactivo_temp= carnet_anterior.folio 
                    area_anterior_temp= person.area
                    rol_anterior_temp= person.rol

                    data_carnet_update = dict(
                        folio= -1,
                        comprobante_motivo = comprobante_motivo,
                        tipoMotivo = tipoMotivo,
                        estado = estado,
                        fecha = datetime.datetime.now(),
                    )
                    carnet_a = CarnetActivoCreate(**data_carnet_update)
                    carnet_a = update_carnetactivo_by_ci (ci_temp,carnet_a,db)
                    
                    data_carnet = dict(
                        folio_desactivo = folio_desactivo_temp,
                        area_anterior= area_anterior_temp,
                        rol_anterior=rol_anterior_temp,
                        )   
                    carnet_eliminado = CarnetEliminadoCreate(**data_carnet)
                    carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=ci_temp)

                else:
                    data_carnet_activo = dict(
                        folio= -1,
                        comprobante_motivo = comprobante_motivo,
                        estado = estado,
                        fecha = datetime.datetime.now(),
                    )       
                    carnet_activo = CarnetActivoCreate(**data_carnet_activo)
                    carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo, db=db, person_ci=ci_temp,tipo_motivo_id=18)

        except Exception as e:
            data_person_con_error = dict(
                        persona_ci= ci_temp,
                        area_con_error = area_temp,
                        error = tipo_error,
                        fecha_error =datetime.datetime.now(),
                        nombre_con_error= nombre_temp,
                        error_simple= error_simple,
                    )       
            carnet_con_errores = CreateCarnet_con_errores(**data_person_con_error)
            carnet_con_errores = create_new_carnet_con_errores(carnet_con_error=carnet_con_errores, db=db)

        count= count +1
    
    

@router.get("/carnetXLotes/{area}/{tipo}/{year}")
def CrearSolicitudCarnetxPorLotes(area: str, tipo : str , year: str ,request: Request , db: Session = Depends(get_db), dbroles: Session = Depends(get_db_roles)):
  try:
     #Si no falla la conexion:
    print("Datos")
    print(area)
    print(tipo)
    print(year)
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        with ThreadPoolExecutor() as executor:
         future = executor.submit(carnet_por_lotes(area,tipo,year,request,db,dbroles))
         username = current_user.nombre_usuario
         accion = "El usuario creó un lote de carnets para la " + area
         tipo = "Crear carnet"
         log = create_new_registro(db, username, accion, tipo)
         return responses.RedirectResponse("/carnets/solicitados", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
  except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")


def buscar_Tipo_Estudiante_carnet(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/student/fileStudent/getStudentAllData/"+ci

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZGlzZXJ0aWMud3Muc2lnZW51OmRpc2VydGljLndzKjIwMTUq",
    "Content-Type": "application/json" 
    }

    payload = json.dumps("")

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)

    result = json.loads(response.text)
    try:
        tipo =result[0]["docentData"]['studentType'] 

        ##print("tipo de estudiante",tipo)
    except Exception as e:
        ##print("no se encontro el estudiante")
        ##print(e)
        raise Exception("No se encontro el tipo de estudiante --> ", ci)

    return tipo