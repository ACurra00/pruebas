from api.endpoints.router_login import get_current_user_from_token
from db.models.usuario import Usuario
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
from webapp.folio.form_folio import FolioForm
from schemas.folio_cont import Folio_ContCreate
from db.repository.folio_cont import update_folio_by_name
from db.repository.folio_cont import buscar_folio_por_nombre
import requests

from db.repository.registro import create_new_registro

templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter

router = APIRouter()

##EndPoints APP
# router.include_router(userRouter, prefix="/user", tags=["Users"])


@router.get("/registrar_folio")
async def crear_folio(request: Request, db: Session = Depends(get_db), folio: str= None):
    #print("tipo de folio",folio)
    numero_1= 0
    numero_2= 0
    numero_3= 0
    numero_4= 0
    numero_5= 0
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)
        current_user: Usuario = get_current_user_from_token(param, db)
        Folio_temp = buscar_folio_por_nombre(folio,db)

        numero_1 = str(Folio_temp.numero_1)  # Convertir a cadena
        numero_2 = str(Folio_temp.numero_2)  # Convertir a cadena
        numero_3 = str(Folio_temp.numero_3)  # Convertir a cadena
        numero_4 = str(Folio_temp.numero_4)  # Convertir a cadena
        numero_5 = str(Folio_temp.numero_5)  # Convertir a cadena

        responseB= templates.TemplateResponse("general_pages/folio/folio.html",{"request": request,"folio": folio,
                                                                                "cont_folio_numero_1" :numero_1,
                                                                                "cont_folio_numero_2" :numero_2,
                                                                                "cont_folio_numero_3" :numero_3,
                                                                                "cont_folio_numero_4" :numero_4,
                                                                                "cont_folio_numero_5" :numero_5,})    
        current_user: Usuario = get_current_user_from_token(param, db)
           
        if ( current_user.rol_usuario == "Carnetizador" or current_user.rol_usuario == "SuperAdmin" or current_user.rol_usuario == "Administrador"):
                return responseB
    except HTTPException:
        return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=503, detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
    except Exception as e:
        raise Exception("Error provocado por el desarrollador  ", e)
        

@router.post("/registrar_folio")
async def crear_folio(request: Request, db: Session = Depends(get_db), folio: str = None):
    #print("estamos en el folio",folio)
    form = FolioForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(token)
            current_user: Usuario = get_current_user_from_token(param, db)
            response = responses.RedirectResponse(
                f"/", status_code=status.HTTP_302_FOUND
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
                update_folio_by_name(folio,
                                     str(form.cont_folio_numero_1),  # Convertir a cadena
                                     str(form.cont_folio_numero_2),  # Convertir a cadena
                                     str(form.cont_folio_numero_3),  # Convertir a cadena
                                     str(form.cont_folio_numero_4),  # Convertir a cadena
                                     str(form.cont_folio_numero_5),  # Convertir a cadena
                                     form.cont_cantidad_hojas,db)
                #print("se guardo correctamente en la base de datos")
                username = current_user.nombre_usuario
                accion = "El usuario actualizó los folios del tipo " + str(folio)
                tipo = "Registrar folios"
                log = create_new_registro(db, username, accion, tipo)
                return response
        except HTTPException:
            return responses.RedirectResponse("login", status_code=status.HTTP_302_FOUND)
        except requests.exceptions.ConnectionError as ce:
            raise HTTPException(status_code=503,
                                detail="Se perdió la conexión con el servidor. Por favor, verifica tu conexión a internet.")
        except Exception as e:
            raise Exception("Error provocado por el desarrollador  " , e)
        
        
