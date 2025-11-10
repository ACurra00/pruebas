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


templates = Jinja2Templates(directory="templates")

# from api.endpoints.web.user import router as userRouter


router = APIRouter()



@router.get("/error/error")
async def home(request: Request, db: Session = Depends(get_db)):
    
    #print ("Estoy en Error")
    error = "Esto es un error"
    response = templates.TemplateResponse(
            "general_pages/error/error.html", {"request": request,
            "error": error
            }
        )
    return response

