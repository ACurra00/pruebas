from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import repository, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/categories/", response_model=list[schemas.CategoriaCarnetVisitante])
def read_categories(skip: int = 0, limit: int = 100000000, db: Session = Depends(get_db)):
    categories = repository.get_categories(db, skip=skip, limit=limit)
    return categories

@app.post("/new_category/", response_model=schemas.CategoriaCarnetVisitante)
def create_category(categoria_carnet_visitante: schemas.CreateCategoriaCarnetVisitante, db: Session = Depends(get_db)):
    db_category = repository.get_category_by_type(db, tipo_categoria=categoria_carnet_visitante.tipo_categoria)
    if db_category:
        raise HTTPException(status_code=400, detail="Ya existe esa categoria registrada")
    return repository.create_category(db=db, categoria_carnet_visitante=categoria_carnet_visitante)


