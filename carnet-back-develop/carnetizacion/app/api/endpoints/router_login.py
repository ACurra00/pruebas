from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,APIRouter
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import status,HTTPException
import requests
from db.models import usuario
from db.repository.usuario import update_state_usuario_by_id_logout
from db.session import get_db
from fastapi import Request
from schemas.token import Token
from db.repository.login import get_user
from core.security import create_access_token
from core.config import settings
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Response    #new
from api.utils import OAuth2PasswordBearerWithCookie    #new
import json
from fastapi import responses 
from fastapi.security.utils import get_authorization_scheme_param

from db.repository.registro import create_new_registro

router = APIRouter()

def authenticate_user(username: str, password: str,db: Session):
    user = get_user(username,db) 
    
    if not user:
        return False
    if not buscarUserLdap(username, password):
        return False
    return user

def buscarUserLdap(usuario: str, password:  str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/login"

    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    "Authorization": "Basic ZnBpY2F5by5zZWM6U2lnZW51X3NlY18qMjAxNCo=",
    "Content-Type": "application/json" 
    }

    payload = json.dumps({
    "username": usuario,
    "password": password
    })
    try:
        response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
        ##print(" falta esta linea")
    except Exception as e:
        ##print(e)
    ##print ("url response "+response.url)
    ##print("status: ")
    ##print(response.status_code)
        a = 1+0
   
    if (response.status_code == 200):
        return True
    else: 
        return False


@router.post("/token", response_model=Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),db: Session= Depends(get_db)):
    name= form_data.username
    password= form_data.password
    ##print("name: "+name +" password: "+password)
   
    usuario = authenticate_user(name, password,db) 

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.nombre_usuario}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)  #set HttpOnly cookie in response
    
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")   #changed to use our implementation

#new function, It works as a dependency
def get_current_user_from_token(
    
    token: str = Depends(oauth2_scheme),
    db: Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error en get current user from token",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:  
        raise credentials_exception
    user = get_user(username,db=db)
    if user is None:
        raise credentials_exception
    return user

@router.post("/refresh_token", response_model=Token)
def refreshToken(request: Request):
    return None

@router.get("/cerrarsesion")
def logout(request: Request, db: Session = Depends(get_db)):
    print("Voy a cerrar sesion")
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
       
        response = responses.RedirectResponse(
            "/login", status_code=status.HTTP_302_FOUND
        )
        try: 
            current_user: usuario = get_current_user_from_token(param, db)
        except HTTPException:
            ##print("No se encontro el usuario")
            response = responses.RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="access_token", value="", httponly=True)
            response.set_cookie(key="refresh_token", value="", httponly=True)
            return response
        
        ##print("El usuario actual es: ", current_user.nombre_usuario)
        
        update_state_usuario_by_id_logout(current_user.id, db)
        ##print("------> cession cerrada <-----")
        
        response.set_cookie(key="access_token", value="", httponly=True)
        response.set_cookie(key="refresh_token", value="", httponly=True)
        username = current_user.nombre_usuario
        accion = "El usuario cerró sesión"
        tipo = "Cerrar sesión"
        log = create_new_registro(db, username, accion, tipo)
        print("Va a ceerar sesion")
        return response
    except Exception as e:
        ##print(e)
        b = 0+1
