from fastapi import APIRouter
from fastapi import Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from db.repository.categoria_carnet_visitante import get_categories
from db.repository.categoria_carnet_visitante import get_category_by_type
from schemas.categoria_carnet_visitante import CategoriaCarnetVisitante
from db.models.categoria_carnet_visitante import Categoria_carnet_visitante
from sqlalchemy.orm import Session
from fastapi.params import Depends
from db.session import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/categoria", response_model=list)
async def categories_list(request: Request, skip: int = 0, limit: int = 100000000, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    return templates.TemplateResponse("templates_visitantes/pages/categoria/catgoria_gestion.html",
                                      {"request": request, "categories": categories})

@router.post("/add")
async def add_category(request: Request, tipo_categoria: str = Form(...), descripcion: str = Form(...), db: Session = Depends(get_db)):
    categoria = Categoria_carnet_visitante(tipo_categoria=tipo_categoria, descripcion=descripcion)
    db.add(categoria)
    db.commit()
    return RedirectResponse(url=router.url_path_for("categories_list"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete_category/{id_category}")
async def delete_category(request: Request, id_category: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria_carnet_visitante).filter(Categoria_carnet_visitante.id == id_category).first()
    db.delete(categoria)
    db.commit()
    return RedirectResponse(url=router.url_path_for("categories_list"), status_code=status.HTTP_303_SEE_OTHER)

@router.get("/edit_category/{id_category}")
async def edit_category(request: Request, id_category: int, skip: int = 0, limit: int = 100000000, db: Session = Depends(get_db)):
    c = db.query(Categoria_carnet_visitante).filter(Categoria_carnet_visitante.id == id_category).first()
    categories = get_categories(db, skip=skip, limit=limit)
    return templates.TemplateResponse("templates_visitantes/pages/categoria/catgoria_gestion.html",
                                      {"request": request, "c": c, "categories": categories})

@router.post("/update_categoria/{id_categoria}")
async def update_category(request: Request, id_categoria: int, tipo_categoria: str = Form(...), descripcion: str = Form(...), db: Session = Depends(get_db)):
    categoria = db.query(Categoria_carnet_visitante).filter(Categoria_carnet_visitante.id == id_categoria).first()
    categoria.tipo_categoria = tipo_categoria
    categoria.descripcion = descripcion
    db.commit()
    return RedirectResponse(url=router.url_path_for("categories_list"), status_code=status.HTTP_303_SEE_OTHER)



