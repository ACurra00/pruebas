import html
import json
import base64
from db.repository.carnet_eliminado import create_new_carnet_eliminado
from db.repository.carnet_activo import create_new_carnet_activo
from schemas.carnet_activo import CarnetActivoCreate
from db.repository.person import create_new_person, retreive_person
from schemas.person import PersonCreate
import requests
from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
from db.repository.tipo_motivos import list_motivos
from db.session import get_db
from db.session import get_db_roles
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from pytest import Session
from db.repository.carnet_activo import get_carnet_by_person
from db.repository.person import update_person_by_ci
from db.repository.carnet_activo import update_carnetactivo_by_ci
from schemas.carnet_eliminado import CarnetEliminadoCreate
from webapp.crear_carnet.form import crearCarnetForm
import pandas
from db.repository.roles_db import get_trabajador_con_cargo

# import treepoem

# from requests import *
from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter

router = APIRouter()


##EndPoints APP
# router.include_router(userRouter, prefix="/user", tags=["Users"])
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

        # print("tipo de estudiante",tipo)
    except Exception as e:
        # print("no se encontro el estudiante")
        # print(e)
        d = 2

    return tipo


def buscar_trabajador_con_cargo(ci: str, db: Session):
    user = get_trabajador_con_cargo(ci, db)
    if not user:
        return False

    return user


def buscar_consejo_universitario_archivo(ci: str, name: str, last_name):
    archivo = 'datos2.xlsx'
    hoja = pandas.read_excel(archivo, engine="openpyxl")
    list = hoja
    last_name_temp = ""
    name_temp = ""
    ci_temp = ""
    cargo_temp = ""
    i = 0
    size = len(list)
    while i < size:
        last_name_temp = list.iloc[i, 3]
        name_temp = list.iloc[i, 2]
        ci_temp = list.iloc[i, 1]
        ci_temp = "" + str(ci_temp)

        if (name_temp == name and last_name_temp == last_name or ci_temp == ci):
            cargo_temp = list.iloc[i, 6]
            # print("se encontro un cargo para esta persona")
            # print(i, " ",ci_temp," " ,name_temp," ",last_name_temp," cargo: ",cargo_temp)
        i += 1

    return cargo_temp

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
        # print("no se encontro el Usuario en esa area")
        return None


def buscarAreas_por_name(text: str, areaID):
    result = json.loads(str(text))
    area = ""
    #areaID = "Ingeniería Civil (CPE)"
    for iter in result:
        if iter['nombre'] == areaID:
            area = iter['idCarrera']
            break

    return area


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


def carnet(area: str, ci: str):
    user = buscar_personas_por_areas_ci(area, ci)
    return user

@router.get("/crearUnMatriculado/{area}/{ci}")
async def crear_carnet(area, ci, request: Request, db: Session = Depends(get_db),
                       dbroles: Session = Depends(get_db_roles)):
 print("Area ma")
 print(area)
 try:
  try:
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    print("Estoy en el get de uno solo")
    areatemp = buscarAreas_por_name(buscarAreas(), area)
    print(areatemp)
    user = carnet(areatemp, ci)
    print("EL usuario es", user)
    temp1 = " "
    temp2 = " "
    temp3 = " "
    temp4 = " "
    temp5 = " "
    print("Estoy en el get de uno solo")
    try:
        temp1 = "se cargaran los datos de la base de datos"

        list_tipo_motivos = list_motivos(db=db)
        carnet_user = get_carnet_by_person(ci, db)
        person_carnet = retreive_person(ci, db)
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)

        temp2 = "se cargo correctamente los datos anteriores"

        temp3 = " se encontro el usuario en la base de datos"

        if user != None:
            rol = ""
            userTemp = user[0]
            print("UserTemp")
            print(user[0])
            temp4 = "PersonType"
            if (userTemp["personType"] == "Student"):
                print("Entra a if de student")
                rol = userTemp["studentType"]
                #rol = "Seminterno"
                print("rol ",rol)

            elif user["personType"] == "Worker":
                temp5 = "personTeacher"
                if user["personTeacher"] == "TRUE":
                    rol = "Docente"

                elif user["personTeacher"] == "FALSE":
                    rol = "No Docente"

            #name_temp = userTemp["name"]
            #last_name = userTemp["surname"] + " " + userTemp["lastname"]
            #print("El nombre es, ", name_temp)
            found = buscar_trabajador_con_cargo(ci, dbroles)

            if found != False and found is not None:
                rol = found.resumen_rol

            print("rol ", rol)
            areatemp = userTemp["area"]
            print("EL area es", areatemp)
            responseB = templates.TemplateResponse("general_pages/crear_carnet.html", {"request": request,
                                                                                       "list_tipo_motivos": list_tipo_motivos,
                                                                                       'user': userTemp,
                                                                                       'area': areatemp,
                                                                                       'carnet_user': carnet_user,
                                                                                       'person_carnet': person_carnet,
                                                                                       'rol': rol})

            current_user: Usuario = get_current_user_from_token(param, db)

            if (current_user.rol_usuario == "Carnetizador" or current_user.rol_usuario == "SuperAdmin"):
                return responseB
    except Exception as e:
        print("Errores --------------")
        # print("")
        # print(temp1)
        # print(temp2)
        # print(temp3)
        # print(temp4)
        # print(temp5)
        # print("hasta aqui llego el error")
        # print("")
        # print(e)
        raise Exception(
            "Error provocado por el desarrollador  " + "temp1: {" + temp1 + "} " + "temp2: {" + temp2 + "} " + "temp3: {" + temp3 + "} " + "temp4: {" + temp4 + "} " + "temp5: {" + temp5 + "} " + "error: ",
            e)
  except HTTPException:
      return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
 except requests.exceptions.ConnectionError as ce:
     raise HTTPException(status_code=503,
                         detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")


@router.post("/crearUnMatriculado/{area}/{ci}")
async def crear_carnet_post(area, ci, request: Request, db: Session = Depends(get_db),
                            dbroles: Session = Depends(get_db_roles)):
 print("Area post ma")
 print(area)
 try:
  try:
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: Usuario = get_current_user_from_token(param, db)
    print("Comenzamos a crear un carnet")
    temp1 = " "
    temp2 = " "
    temp3 = " "
    temp4 = " "
    temp5 = " "
    areatemp = buscarAreas_por_name(buscarAreas(), area)
    print("Coge area temp")
    print(areatemp)
    print("Antes del form")
    form = crearCarnetForm(request)
    print("Coge form")
    print(form)
    print("Antes del load")
    await form.load_data()
    print("Despues del load")
    if await form.is_valid():
        try:

            usuario = carnet(areatemp, ci)
            print("El usuario es en post", usuario)
            user = usuario[0]
            # print("se encontro el usuario")
            person = retreive_person(ci, db)
            carnet_anterior = get_carnet_by_person(ci, db)

            form.ci = html.escape(user['identification'])
            form.area = html.escape(user['area'])

            temp1 = "se encontro el usuario"

            if (user["personType"] == "Student"):
                form.rol = html.escape(user["studentType"])
                #form.rol = "Seminterno"
                form.annoEstudiantePersona = html.escape(user['studentYear'])
                form.tipoPersona = "Estudiante"

            #found = buscar_trabajador_con_cargo(ci, dbroles)
            temp2 = "temp2"

            #if found != False:
                # print("Se encontro cargo para el usuario")
                # print(found)
                #form.rol = found

            form.nombre = user['name'] + " " + user['surname'] + " " + user['lastname']

            # =====================================================

            form.folio = None  # se desactivo el folio, es null
            # print("")
            print ("folio desactivado del formulario")
            # print("")

            # =====================================================

            print("===========Datos del usuario======================")
            print("ci: ",form.ci)
            ##print("folio ",form.folio)
            if carnet_anterior != None:
                d = 3
                print("folio desactivo ",carnet_anterior.folio)
            else:
                t = 1
                print("folio desactivo: No existe folio anterior")
                r = 1
            print("area ",form.area)

            if person is None:
                r = 2
                print("area anterior: "+"No existe Area anteriror")
            else:
                f = 1
                print("area anterior ",person.area)

            print("comprobante motivo: ",form.comprobante_motivo)
            print("estado ",form.estado)
            if (user["personType"] == "Student"):
                f = 2
                # print("anno estudiante ",form.annoEstudiantePersona)
            print("nombre ",form.nombre)
            print("rol ",form.rol)
            print("tipo de persona ",form.tipoPersona)

            if person is None:
                g = 0
                print("rol anterior","No existe Rol anterior")
            else:
                h = 0
                print("rol anterior",person.rol)

            print("motivo",form.tipoMotivo)
            print("comprobante motivo: ",form.comprobante_motivo)
            temp3 = "todo ok 3"
            print("============== Estos son los datos que se recogieron==========")

            if person is None:
                print("no existe la persona en el registro")
                print("se registrara")

                person_a = PersonCreate(**form.__dict__)
                person_a = create_new_person(person_a, db)
                print("Impriemiendo la persona Creada------")
                print("persona: ",person_a.nombre)
                print("persona: ", person_a.area)
                print("persona: ", person_a.ci)
                print("persona: ", person_a.is_activa)
                print("persona: ", person_a.rol)

            else:
                if carnet_anterior is not None:
                 print("El folio es none")
                 form.folio_desactivo = html.escape(str(carnet_anterior.folio))
                else:
                 form.folio_desactivo = ""
                form.area_anterior = html.escape(person.area)
                form.rol_anterior = html.escape(person.rol)

                person_a = PersonCreate(**form.__dict__)

                person_a = update_person_by_ci(ci, person_a, db)
                print("Se actualizo la persona")
            temp4 = "se actualizo a la persona"
            if carnet_anterior is not None:  # si tiene carnet anterior
                # print("existia un carnet anterior y se actualizara")
                form.folio_desactivo = html.escape(str(carnet_anterior.folio))
                form.area_anterior = html.escape(person.area)
                form.rol_anterior = html.escape(person.rol)
                form.estado = "Solicitado"
                form.folio = -1
                carnet_a = CarnetActivoCreate(**form.__dict__)
                carnet_a = update_carnetactivo_by_ci(ci, carnet_a, db)

                carnet_eliminado = CarnetEliminadoCreate(**form.__dict__)
                carnet_eliminado = create_new_carnet_eliminado(carnet_eliminado=carnet_eliminado, db=db, person_ci=ci)
                # print("se actualizo el nuevo carnet y se guardo el viejo")
            else:
                # print("El usuario no tenia carnet activo")
                form.folio = -1

                carnet_activo = CarnetActivoCreate(**form.__dict__)
                carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo, db=db, person_ci=ci,
                                                         tipo_motivo_id=form.tipoMotivo)

            temp5 = "carnet todo ok"

            print("Carne Realizado correctamente")
            # responseB= templates.TemplateResponse("general_pages/carnets/carnets_pendientes.html",{"request": request, "carnets": carnets, "persons":persons, "motivos":motivos})

            username = current_user.nombre_usuario
            accion = "El usuario creó un carnet para la " + area
            tipo = "Crear carnet"
            log = create_new_registro(db, username, accion, tipo)
            return responses.RedirectResponse("/carnets/solicitados", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            # print("Errores --------------")
            # print("")
            # print(temp1)
            # print(temp2)
            # print(temp3)
            # print(temp4)
            # print(temp5)
            # print("hasta aqui llego el error")
            # print("")
            # print(e)
            raise Exception(
                "Error provocado por el desarrollador  " + "temp1: {" + temp1 + "} " + "temp2: {" + temp2 + "} " + "temp3: {" + temp3 + "} " + "temp4: {" + temp4 + "} " + "temp5: {" + temp5 + "} " + "error: ",
                e)
  except HTTPException:
      return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
 except requests.exceptions.ConnectionError as ce:
     raise HTTPException(status_code=503,
                         detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")