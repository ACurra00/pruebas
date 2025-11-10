from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
from schemas.registro import RegistroCreate
from db.models.registro import Registro
from sqlalchemy import select
from datetime import datetime


def create_new_registro(db: Session, username: str, accion: str, tipo: str):
    registro_iobject = Registro(username=username, accion=accion, tipo=tipo)
    db.add(registro_iobject)
    db.commit()
    db.refresh(registro_iobject)
    return registro_iobject


def lista_registro(db: Session):
    registro = db.query(Registro).all()
    return registro


def lista_registros_filtrado_por_todos(
    db: Session,
    username: str = None,
    fecha_inicio: date = None,
    fecha_fin: date = None,
    tipo: str = None
):
    query = db.query(Registro).distinct()

    if username and username.strip():
        query = query.filter(Registro.username.ilike(f'%{username}%'))

    if tipo and tipo != "Seleccione":
        query = query.filter(Registro.tipo == tipo)

    if fecha_inicio and fecha_fin:
        query = query.filter(Registro.fecha.between(fecha_inicio, fecha_fin))

    return query.order_by(desc(Registro.id)).all()


def lista_filtrados_por_usuario(db: Session, username: str = None):
    query = db.query(Registro).distinct()
    registro_filtro = query.filter(Registro.username == username).order_by(desc(Registro.id))
    return registro_filtro


def lista_filtrados_por_tipo(db: Session, tipo: str = None):
    query = db.query(Registro).distinct()
    registro_filtro = query.filter(Registro.tipo == tipo).order_by(desc(Registro.id))
    return registro_filtro


def lista_filtrados_por_fecha(db: Session, fecha: date = None):
    query = db.query(Registro).distinct()
    registro_filtro = query.filter(Registro.fecha == fecha).order_by(desc(Registro.id))
    return registro_filtro


def lista_filtrados_por_fecha_rango(db: Session, fecha_inicio: date = None, fecha_fin: date = None):
    query = db.query(Registro).distinct()
    if fecha_inicio and fecha_fin:
        query = query.filter(Registro.fecha.between(fecha_inicio, fecha_fin))
    registro_filtro = query.order_by(desc(Registro.fecha)).all()
    return registro_filtro
