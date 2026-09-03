from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AnimalDetail, AnimalSummary
from app.services import queries
from app.utils.errors import AppError

router = APIRouter(prefix="/animals", tags=["animals"])


@router.get("", response_model=list[AnimalSummary])
def get_animals(include_demo: bool = Query(True), db: Session = Depends(get_db)):
    return queries.list_animals(db, include_demo=include_demo)


@router.get("/{animal_id}", response_model=AnimalDetail)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    detail = queries.animal_detail(db, animal_id)
    if detail is None:
        raise AppError("Animal not found.", status_code=404, code="not_found")
    return detail
