from multiprocessing import current_process
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status

from db.session import get_db
from db.models.carnet_activo import CarnetActivo
from schemas.carnet_activo import CarnetActivoCreate,ShowCarnetActivo
from db.repository.carnet_activo import create_new_carnet_activo

router = APIRouter()


@router.post("/crear-carnet_activo/",response_model=ShowCarnetActivo)
def create_carnet_activo(carnet_activo: CarnetActivoCreate,db: Session = Depends(get_db)):
    current_person = "01021268345"
    current_motivo= 3
    carnet_activo = create_new_carnet_activo(carnet_activo=carnet_activo,db=db,person_ci=current_person, tipo_motivo_id=current_motivo)
    return carnet_activo
