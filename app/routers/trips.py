from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.auth import get_current_user
from app.database import SessionLocal
from app.services.settlement import calculate_settlement
from app import models

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

@router.get("/{trip_id}/settlement", response_model=List[schemas.Settlement])
def get_settlement(trip_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
     # Optional: Verify the current_user is part of the trip
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    user_ids = [member.id for member in trip.members]
    if current_user.id not in user_ids:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")
    return calculate_settlement(trip_id, db)
    

