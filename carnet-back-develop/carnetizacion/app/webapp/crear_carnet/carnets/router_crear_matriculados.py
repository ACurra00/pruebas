import json
import requests
import base64
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
from db.repository.person import create_new_person, retreive_person, update_person_by_ci
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


@router.get("/matriculados/crear")
async def home(request: Request, db: Session = Depends(get_db), page: int = 1, area2: str = None):
    print("aqiui estopy en el matriculados")
    try:
        ###print(page, area2)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        is_x_lotes = False
        lista_areas, count = listaAreas(buscarAreas())
        print("Lista areas en matriculados")
        print(listaAreas(buscarAreas()))
        print("Buscar areas en matriculados")
        print(buscarAreas())
        total_areas = count
        listResult = []
        page_number = 1
        if (page > 0 and area2 != "" and area2 is not None):
            ###print("esto aqui en el paginado")
            is_x_lotes = True
            areatemp = buscarAreas_por_name(buscarAreas(), area2)
            print("areatemp")
            print(areatemp)
            listResult = carnet_x_lote(areatemp)
            page_number = page
        else:
            listResult = []

        paginator = Paginator(listResult, 20)  # 6 employees per page

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)

        response = templates.TemplateResponse(
            "general_pages/carnets/crear_carnet_xlotes_matriculados.html",
            {"request": request, 'area': area2, "total_areas": total_areas, "lista_areas": lista_areas,
             "page_obj": page_obj, "is_x_lotes": is_x_lotes})

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
        print(e)
        ###print("Error Home")
        raise Exception("Error provocado por el desarrollador  ", e)
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")


def listaAreas(text: str):
    result = json.loads(str(text))
    lista = ""
    count = 0
    for iter in result:
        iter['nombre']
        count = count + 1
        lista = lista + iter['nombre'] + ","

    return lista, count


def buscarAreas_por_name(text: str, areaID):
    result = json.loads(str(text))
    area = ""
    #areaID = "Ingeniería Civil (CPE)"
    for iter in result:
        if iter['nombre'] == areaID:
            area = iter['idCarrera']
            break

    return area


def buscar_personas_por_areas(area: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/dss/search-matriculate"

    # Extrae las credenciales de autenticación del nuevo endpoint
    username = "disertic-web"
    password = "disertic-web841109"

    # Construye la autorización básica
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headersList = {
        "Accept": "*/*",
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }

    # Prepara el payload con el id de la carrera
    payload = {
        "identification": "",
        "lastName": "",
        "firstName": "",
        "middleName": "",
        "idCareer": area,  # Utiliza el parámetro 'area' como idCareer
        "idCourseType": "",
        "idSex": "",
        "idEntrySource": "",
        "idStudentStatus": ""
    }

    response = requests.request("POST", reqUrl, data=json.dumps(payload), headers=headersList)
    #print(response.text)
    users = json.loads(response.text)

    return users

#Para buscar uno solo por area y ci:
def buscar_personas_por_areas_ci(area: str, ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/dss/search-matriculate"

    # Extrae las credenciales de autenticación del nuevo endpoint
    username = "disertic-web"
    password = "disertic-web841109"

    # Construye la autorización básica
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headersList = {
        "Accept": "*/*",
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }

    # Prepara el payload con el id de la carrera
    payload = {
        "identification": ci,
        "lastName": "",
        "firstName": "",
        "middleName": "",
        "idCareer": area,  # Utiliza el parámetro 'area' como idCareer
        "idCourseType": "",
        "idSex": "",
        "idEntrySource": "",
        "idStudentStatus": ""
    }

    response = requests.request("POST", reqUrl, data=json.dumps(payload), headers=headersList)
    #print(response.text)
    users = json.loads(response.text)

    return users

def buscarTrabajdor_and_Estudiante(ci: str, area: str):
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

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    result = json.loads(str(response.text))
    if (bool(result)):
        return result
    else:
        ###print("no se encontro el Usuario en esa area")
        return None


def buscarAreas():
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/dss/getcareermodel"

    # Extrae las credenciales de autenticación del nuevo endpoint
    username = "disertic-web"
    password = "disertic-web841109"

    # Construye la autorización básica
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headersList = {
        "Accept": "*/*",
        "Authorization": f"Basic {encoded_auth}"
    }

    response = requests.request("GET", reqUrl, headers=headersList)

    return response.text

def carnet_para_Persona(area: str, ci: str):
    if area != "":
        ###print("Area Encontrada")
        usuario = buscarTrabajdor_and_Estudiante(ci, area)
        if usuario is not None:
            return [usuario[0]]
        else:
            ###print("No se encontro el usuario")
            c = 1 + 0


def carnet_x_lote(area: str):
    userstemp = buscar_personas_por_areas(area)

    return userstemp

def carnet(area: str, ci: str):
    user = buscarAreas(area, ci)
    return user



@router.post("/matriculados/crear")
async def home(request: Request, db: Session = Depends(get_db), page: int = 1):
  try:
    print("aqiui estopy en el matriculados post")
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    form = BuscarPersonaForm(request)
    lista_areas, count = listaAreas(buscarAreas())
    total_areas = count
    is_x_lotes = False
    listResult = []
    await form.load_data()
    value = form.is_valid()
    if value:
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)

            area = buscarAreas_por_name(buscarAreas(), form.areaBuscarPersona)
            ###print("area",area)
            ###print ("Procesando la busqueda de persona")
            ###print("La  busqueda es: ", form.tipoBuscarPersona)
            ci = form.ciBuscarPersona

            if (form.tipoBuscarPersona == "carnet_x_lotes_off"):
                is_x_lotes = False

                users = buscar_personas_por_areas_ci(area, ci)


                if not users:  # Comprueba si users está vacío
                    # Maneja el caso en que no se encuentren usuarios
                    print("No encuentro un matriculado")
                    page_number = page
                    paginator = Paginator(listResult, 20)
                    page_obj = paginator.page(paginator.num_pages)
                    error_no_encontrado = "No se encontraró al estudiante en el área especificada"
                    return templates.TemplateResponse(
                        "general_pages/carnets/crear_carnet_xlotes_matriculados.html",
                        {
                            'request': request,
                            'users': [],
                            'area': form.areaBuscarPersona,
                            "lista_areas": lista_areas,
                            "total_areas": total_areas, "page_obj": page_obj,
                            'error_no_encontrado': error_no_encontrado
                        })




                print(users[0])
                listResult.append(users[0])
                page_number = page
                paginator = Paginator(listResult, 20)  # 20 employees per page

                try:

                    page_obj = paginator.page(page)

                except PageNotAnInteger:
                    # if page is not an integer, deliver the first page
                    page_obj = paginator.page(1)
                except requests.exceptions.ConnectionError as ce:
                    raise HTTPException(status_code=503,
                                        detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
                except EmptyPage:
                    # if the page is out of range, deliver the last page
                    page_obj = paginator.page(paginator.num_pages)
                responsePersona = templates.TemplateResponse("general_pages/carnets/crear_carnet_xlotes_matriculados.html",
                                                             {'request': request, 'users': users,
                                                              'area': form.areaBuscarPersona,
                                                              "lista_areas": lista_areas,
                                                              "total_areas": total_areas, "page_obj": page_obj,
                                                              "is_x_lotes": is_x_lotes
                                                              })
                return responsePersona


            elif (form.tipoBuscarPersona == "carnet_x_lotes_on"):
                is_x_lotes = True

                print("Estamos en carnet por lotes")
                ###print ("El area es: ", area)
                ###print("valores capturados: ")
                ##print(form.student_year)
                ##print(form.tipoBuscarCarnet)

                listResult = carnet_x_lote(area)

                page_number = page
                paginator = Paginator(listResult, 20)  # 20 employees per page

                try:

                    page_obj = paginator.page(page_number)

                except PageNotAnInteger:
                    # if page is not an integer, deliver the first page
                    page_obj = paginator.page(1)
                except EmptyPage:
                    # if the page is out of range, deliver the last page
                    page_obj = paginator.page(paginator.num_pages)
                if listResult == []:
                    error_no_encontrado = "No se encontraron estudiantes en el area especificada"
                    return templates.TemplateResponse("general_pages/carnets/crear_carnet_xlotes_matriculados.html",
                                                                      {'request': request, "page_obj": page_obj,
                                                                       'area': form.areaBuscarPersona,
                                                                       "lista_areas": lista_areas,
                                                                       "total_areas": total_areas,
                                                                       "error_no_encontrado": error_no_encontrado
                                                                       })

                responses_carnet_x_lotes = templates.TemplateResponse("general_pages/carnets/crear_carnet_xlotes_matriculados.html",
                                                                      {'request': request, "page_obj": page_obj,
                                                                       'area': form.areaBuscarPersona,
                                                                       "lista_areas": lista_areas,
                                                                       "total_areas": total_areas,
                                                                       "is_x_lotes": is_x_lotes
                                                                       })
                return responses_carnet_x_lotes


        except HTTPException as e:
            ##print("Error en Home")
            ##print (e)
            response = templates.TemplateResponse(
                "general_pages/homepage.html",
                {"request": request,
                 "total_areas": total_areas,
                 "lista_areas": lista_areas,
                 "page_obj": page_obj,
                 "is_x_lotes": is_x_lotes,
                 })
            return response

    else:
        listResult = []
        paginator = Paginator(listResult, 20)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        errorArea = form.errorArea
        errorCI = form.errorCI
        errorFiltro = form.errorFiltro
        erroryear = form.erroryear

        response = templates.TemplateResponse(
            "general_pages/carnets/crear_carnet_xlotes_matriculados.html",
            {"request": request,
             "total_areas": total_areas,
             "lista_areas": lista_areas,
             "errorArea": errorArea,
             "page_obj": page_obj,
             "is_x_lotes": is_x_lotes,
             "errorCI": errorCI,
             "errorFiltro": errorFiltro,
             "erroryear": erroryear})
        return response
  except HTTPException:
      return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
  except requests.exceptions.ConnectionError as ce:
      raise HTTPException(status_code=503,
                          detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")


def carnet_por_lotes(area: str, request: Request, db: Session = Depends(get_db),
                     dbroles: Session = Depends(get_db_roles)):
    tipo_error = "Unknown"
    error_simple = "Desconocido"
    areatemp = buscarAreas_por_name(buscarAreas(), area)
    areaID = areatemp
    listResult = carnet_x_lote(areatemp)
    count = 1
    for user in listResult:
      try:
           ci_temp = user['identification']
           year = user['studentYear']
           #area_temp = area
           area_temp = user['area']
           comprobante_motivo = "carnets creado x Lotes"
           estado = "Solicitado"
           tipoMotivo = "Carnet x Lotes"

           carnet_anterior = get_carnet_by_person(ci_temp, db)

           if(areaID == "-66de03e8:12ae39077ab:-279b"):
             area_temp = "Facultad de Ingeniería Informática"

           person = retreive_person(ci_temp, db)


           try:
             print("En el primer try")
             nombre_temp = user['name'] + " " + user['surname'] + " " + user['lastname']
             print(nombre_temp)
           except Exception:
             print("Error en el nombre")
             tipo_error = "Name Problem"
             error_simple = "Problema con el nombre o apellido"
             nombre_temp = "Uknown"
             raise Exception("Error provocado por el desarrollador")

           try:
             rol_temp = user["studentType"]
           except Exception:
             print ("Error en el tipo de estudiante : ->",ci_temp)
             tipo_error = "Student Type Problem"
             error_simple = "Tipo de estudiante Desconocido"
             raise Exception("Error provocado por el desarrollador")

           try:
             year = user['studentYear']
           except Exception:
             print ("Error en personar studentYear person : ->",ci_temp)
             tipo_error = "Student Year Problem"
             error_simple = "Problema con el anno"
             raise Exception("Error provocado por el desarrollador")



           if person is None:
             print("En el primer if de persona")
             data_person = dict(
             ci=ci_temp,
             nombre=nombre_temp,
             area=area_temp,
             rol=rol_temp,
             )
             person_a = PersonCreate(**data_person)
             person_a = create_new_person(person_a, db)
           else:
             print("En el segundo if de persona")
             print("En el medio del if de persona")
             data_person = dict(
                ci=ci_temp,
                nombre=nombre_temp,
                area=area_temp,
                rol=rol_temp,
             )
             print("Creandola")
             person_a = PersonCreate(**data_person)
             print("QUasi creada")
             person_a = update_person_by_ci(ci_temp, person_a, db)
             print("Ya se update")


           print("JUSTO ANTES DEL IF")
           if carnet_anterior is None:
             print("En el primer if de carnet")
             data_carnet_activo = dict(
              folio=-1,
              comprobante_motivo=comprobante_motivo,
              estado=estado,
              fecha=datetime.datetime.now(),
             )
             carnet_activo = CarnetActivoCreate(**data_carnet_activo)
             carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo, db=db, person_ci=ci_temp,
                                                             tipo_motivo_id=18)
             print("estoy creandolo first")
           else:
             print("En el segundo if de carnet")
             folio_desactivo_temp = carnet_anterior.folio
             area_anterior_temp = person.area
             rol_anterior_temp = person.rol

             data_carnet_update = dict(
                folio=-1,
                comprobante_motivo=comprobante_motivo,
                tipoMotivo=tipoMotivo,
                estado=estado,
                fecha=datetime.datetime.now(),
             )
             print("estoy creandolo first")

             carnet_a = CarnetActivoCreate(**data_carnet_update)
             carnet_a = update_carnetactivo_by_ci(ci_temp, carnet_a, db)

             data_carnet = dict(
                folio_desactivo=folio_desactivo_temp,
                area_anterior=area_anterior_temp,
                rol_anterior=rol_anterior_temp,
              )
             carnet_eliminado = CarnetEliminadoCreate(**data_carnet)
             carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=ci_temp)

      except Exception as e:
          data_person_con_error = dict(
          persona_ci=ci_temp,
          area_con_error=area_temp,
          error=tipo_error,
          fecha_error=datetime.datetime.now(),
          nombre_con_error=nombre_temp,
          error_simple=error_simple,
          )
          print("Este fulano tiene error " + nombre_temp)
          carnet_con_errores = CreateCarnet_con_errores(**data_person_con_error)
          carnet_con_errores = create_new_carnet_con_errores(carnet_con_error=carnet_con_errores, db=db)

      count = count + 1


@router.get("/carnetXLotesMatriculados/{area}")
def CrearSolicitudCarnetxPorLotes(area: str, request: Request, db: Session = Depends(get_db),
                                  dbroles: Session = Depends(get_db_roles)):
  try:
    #Si no falla la conexion:
    try:
     token = request.cookies.get("access_token")
     scheme, param = get_authorization_scheme_param(token)
     current_user: Usuario = get_current_user_from_token(param, db)
     with ThreadPoolExecutor() as executor:
       future = executor.submit(carnet_por_lotes(area, request, db, dbroles))
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
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/student/fileStudent/getStudentAllData/" + ci

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": "Basic ZGlzZXJ0aWMud3Muc2lnZW51OmRpc2VydGljLndzKjIwMTUq",
        "Content-Type": "application/json"
    }

    payload = json.dumps("")

    response = requests.request("GET", reqUrl, data=payload, headers=headersList)

    result = json.loads(response.text)
    try:
        tipo = result[0]["docentData"]['studentType']

        ##print("tipo de estudiante",tipo)
    except Exception as e:
        ##print("no se encontro el estudiante")
        ##print(e)
        raise Exception("No se encontro el tipo de estudiante --> ", ci)

    return tipo