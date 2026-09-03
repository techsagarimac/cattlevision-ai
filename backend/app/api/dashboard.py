from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DashboardResponse
from app.services import queries

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(include_demo: bool = Query(True), db: Session = Depends(get_db)):
    return queries.dashboard(db, include_demo=include_demo)
