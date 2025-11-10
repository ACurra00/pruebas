from typing import Generator

import sqlalchemy
from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
SQLALCHEMY_DATABASE_ROLES = settings.DATABASE_ROLES

engine = create_engine(SQLALCHEMY_DATABASE_URL)
roles = create_engine(SQLALCHEMY_DATABASE_ROLES)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionRoles = sessionmaker(autocommit=False, autoflush=False, bind=roles)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_db_roles() -> Generator:
    try:
        db = SessionRoles()
        yield db
    finally:
        db.close()
