from fastapi import APIRouter
from fastapi import Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.models.estado_carnet_visitante import Estado_carnet_visitante
from db.repository.estado_carnet_visitante import get_estados
from sqlalchemy.orm import Session
from fastapi.params import Depends
from db.session import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/estado")
async def estado_list(request: Request, db: Session = Depends(get_db)):
    estados = db.query(Estado_carnet_visitante).order_by(Estado_carnet_visitante.id.asc())
    return templates.TemplateResponse("templates_visitantes/pages/estado/estado_gestion.html",
                                      {"request": request, "estados": estados})


@router.post("/add_estado")
async def add_estado(request: Request, db: Session = Depends(get_db), estado: str = Form(...),
                     descripcion: str = Form(...)):
    estado = Estado_carnet_visitante(estado=estado, descripcion=descripcion)
    db.add(estado)
    db.commit()
    return RedirectResponse(url=router.url_path_for("estado_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete_estado/{id_estado}")
async def delete_estado(request: Request, id_estado: int, db: Session = Depends(get_db)):
    estado = db.query(Estado_carnet_visitante).filter(Estado_carnet_visitante.id == id_estado).first()
    db.delete(estado)
    db.commit()
    return RedirectResponse(url=router.url_path_for("estado_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit_estado/{id_estado}")
async def edit_estado(request: Request, id_estado: int, skip: int = 0, limit: int = 100000000,
                        db: Session = Depends(get_db)):
    e = db.query(Estado_carnet_visitante).filter(Estado_carnet_visitante.id == id_estado).first()
    estados = get_estados(db, skip=skip, limit=limit)
    return templates.TemplateResponse("templates_visitantes/pages/estado/estado_gestion.html",
                                      {"request": request, "e": e, "estados": estados})


@router.post("/update_estado/{id_estado}")
async def update_estado(request: Request, id_estado: int, estado: str = Form(...), descripcion: str = Form(...),
                          db: Session = Depends(get_db)):
    est = db.query(Estado_carnet_visitante).filter(Estado_carnet_visitante.id == id_estado).first()
    est.estado = estado
    est.descripcion = descripcion
    db.commit()
    return RedirectResponse(url=router.url_path_for("estado_list"), status_code=status.HTTP_303_SEE_OTHER)
