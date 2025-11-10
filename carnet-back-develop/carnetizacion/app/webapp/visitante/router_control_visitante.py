from fastapi import APIRouter
from fastapi import Request, status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models.carnet_visitante import Carnet_visitante
from db.models.categoria_carnet_visitante import Categoria_carnet_visitante
from db.repository.categoria_carnet_visitante import get_categories
from db.repository.estado_carnet_visitante import get_estados
from db.repository.carnet_visitante import get_visitantes
from db.repository.carnet_visitante import create_visitante
from schemas.carnet_visitante import CarnetVisitante
from sqlalchemy.orm import Session
from fastapi.params import Depends
from db.session import get_db
from datetime import date

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/visitante")
async def vistantes_list(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100000000):
    visitantes = db.query(Carnet_visitante).join(Carnet_visitante.categoria).join(Carnet_visitante.estado).order_by(Carnet_visitante.id.asc())
    categories = get_categories(db, skip=skip, limit=limit)
    estados = get_estados(db, skip=skip, limit=limit)
    return templates.TemplateResponse("templates_visitantes/pages/visitante/control_visitante.html",
                                      {"request": request, "visitantes": visitantes, "categories": categories,
                                       "estados": estados})


@router.post("/add_visitante")
async def add_visitante(request: Request, db: Session = Depends(get_db), nombre: str = Form(...),
                        identificacion: str = Form(...), motivo_visita: str = Form(...), area_destino: str = Form(...),
                        categoria_carnet: int = Form(...), estado_carnet: int = Form(...), folio: str = Form(...),
                        fecha_entrada: date = Form(...), fecha_salida: date = Form(...)):
    visitante = Carnet_visitante(nombre=nombre, identificacion=identificacion, motivo_visita=motivo_visita,
                                 area_destino=area_destino, categoria_carnet=categoria_carnet,
                                 estado_carnet=estado_carnet, folio=folio, fecha_entrada=fecha_entrada,
                                 fecha_salida=fecha_salida)
    db.add(visitante)
    db.commit()
    return RedirectResponse(url=router.url_path_for("vistantes_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete_visitante/{id_visitante}")
async def delete_category(request: Request, id_visitante: int, db: Session = Depends(get_db)):
    visitante = db.query(Carnet_visitante).filter(Carnet_visitante.id == id_visitante).first()
    db.delete(visitante)
    db.commit()
    return RedirectResponse(url=router.url_path_for("vistantes_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit_visitante/{id_visitante}")
async def edit_visitante(request: Request, id_visitante: int, skip: int = 0, limit: int = 100000000,
                         db: Session = Depends(get_db)):
    v = db.query(Carnet_visitante).join(Carnet_visitante.categoria).join(Carnet_visitante.estado).filter(Carnet_visitante.id == id_visitante).first()
    visitantes = get_visitantes(db, skip=skip, limit=limit)
    categorias = get_categories(db, skip=skip, limit=limit)
    estados = get_estados(db, skip=skip, limit=limit)
    return templates.TemplateResponse("templates_visitantes/pages/visitante/control_visitante.html",
                                      {"request": request, "v": v, "visitantes": visitantes, "categorias": categorias, "estados": estados})


@router.post("/update_visitantes/{id_visitantes}")
async def update_visitante(request: Request, id_visitantes: int, nombre: str = Form(...),
                           identificacion: str = Form(...), motivo_visita: str = Form(...),
                           area_destino: str = Form(...),
                           categoria_carnet: int = Form(...), estado_carnet: int = Form(...), folio: str = Form(...),
                           fecha_entrada: date = Form(...), fecha_salida: date = Form(...),
                           db: Session = Depends(get_db)):
    visitante = db.query(Carnet_visitante).filter(Carnet_visitante.id == id_visitantes).first()
    visitante.nombre = nombre
    visitante.identificacion = identificacion
    visitante.motivo_visita = motivo_visita
    visitante.area_destino = area_destino
    visitante.categoria_carnet = categoria_carnet
    visitante.estado_carnet = estado_carnet
    visitante.folio = folio
    visitante.fecha_entrada = fecha_entrada
    visitante.fecha_salida = fecha_salida
    db.commit()
    return RedirectResponse(url=router.url_path_for("vistantes_list"), status_code=status.HTTP_303_SEE_OTHER)
