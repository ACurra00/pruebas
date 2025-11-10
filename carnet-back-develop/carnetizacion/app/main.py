from api.api import api_router
from core.config import settings
from db.base import Base
from db.session import engine
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from webapp.base import api_router as web_app_router
from fastapi import Request
import logging
from fastapi.templating import Jinja2Templates
import sys,traceback


logging.basicConfig(handlers=[logging.FileHandler(filename='./logs/api.log', encoding='utf-8')], level=logging.DEBUG)



def create_tables():
    
    Base.metadata.create_all(bind=engine)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    
    include_router(app)
    configure_static(app)
    middleware(app)
    create_tables()
    return app


origins = []

app = start_application()

@app.exception_handler(Exception)
async def catch_exception_handler(request: Request, exc: Exception):
    logging.error(exc)
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    error = repr(traceback.extract_tb(exc_traceback))
    exceptionn = exc
   

    
    templates = Jinja2Templates(directory="templates")
    response = templates.TemplateResponse(
            "general_pages/error/error.html", {"request": request,
            "error": error,
            "exceptionn": exceptionn
            }
        )
    return response
