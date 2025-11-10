from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status

from db.session import get_db
from db.models.person import Person
from schemas.person import PersonCreate,ShowPerson
from db.repository.person import create_new_person

router = APIRouter()


@router.post("/crear-person/",response_model=ShowPerson)
def create_person(person: PersonCreate,db: Session = Depends(get_db)):
    person = create_new_person(person=person,db=db)
    return person
