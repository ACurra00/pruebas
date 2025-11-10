from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/home_visitante")
async def home(request: Request):
	return templates.TemplateResponse("templates_visitantes/pages/home.html", {"request": request})