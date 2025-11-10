from sqlalchemy.orm import Session
from schemas.categoria_carnet_visitante import CategoriaCarnetVisitante, CreateCategoriaCarnetVisitante
from db.models.categoria_carnet_visitante import Categoria_carnet_visitante


def get_categories(db: Session, skip: int = 0, limit: int = 100000000):
    return db.query(Categoria_carnet_visitante).offset(skip).limit(limit).all()

def create_category(db: Session, categoria_carnet_visitante: CreateCategoriaCarnetVisitante):
    db_categoria_carnet_visitante = Categoria_carnet_visitante(tipo_categoria=categoria_carnet_visitante.tipo_categoria, descripcion=categoria_carnet_visitante.descripcion)
    db.add(db_categoria_carnet_visitante)
    db.commit()
    db.refresh(db_categoria_carnet_visitante)
    return db_categoria_carnet_visitante

def get_category_by_type(db: Session, tipo_categoria: str):
    return db.query(Categoria_carnet_visitante).filter(Categoria_carnet_visitante.tipo_categoria == tipo_categoria).first()
