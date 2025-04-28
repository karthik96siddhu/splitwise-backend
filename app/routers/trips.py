from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.auth import get_current_user
from app.database import SessionLocal

router = APIRouter(prefix="/trips", tags=["trips"])

# Dependency to get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.TripResponse)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.create_trip(db=db, trip=trip, user_id=current_user.id)

@router.post("/{trip_id}/add-member/{user_id}")
def add_member(trip_id: int, user_id: int, db: Session = Depends(get_db), current_user= Depends(get_current_user)):
    trip  = crud.add_memebr_to_trip(db, trip_id, user_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip or User not found")
    return {"message": "User added to trip successfully"}

