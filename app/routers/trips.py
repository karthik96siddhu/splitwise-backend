from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
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
    trip  = crud.add_member_to_trip(db, trip_id, user_id)
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

@router.post("/{trip_id}/invite", response_model=schemas.UserResponse)
def invite_trip_member_by_email(
    trip_id: int,
    request: schemas.AddMemberByEmailRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only Trip creator can add members")
    
    user_to_add = db.query(models.User).filter(models.User.email == request.email).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="No user found with this email")
    if user_to_add in trip.members:
        raise HTTPException(status_code=400, detail="User already in trip")
    trip.members.append(user_to_add)
    db.commit()
    db.refresh(trip)
    return user_to_add

@router.delete("/trips/members", response_model=schemas.UserResponse)
def remove_trip_member(
    trip_id: int,
    request: schemas.RemoveMemeberByEmailRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only Trip creator can remove members")
    user_to_remove = db.query(models.User).filter(models.User.email == request.email).first()
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="No user found with this email")
    if user_to_remove not in trip.members:
        raise HTTPException(status_code=400, detail="User not in trip")
    
    # check for existing expenses by this user in this trip
    has_expenses = db.query(models.Expense).filter(
        models.Expense.trip_id == trip.id,
        models.Expense.payer_id == user_to_remove.id
    ).first()
    if has_expenses:
        raise HTTPException(status_code=400, detail="User has expenses in this trip, cannot remove")
    trip.members.remove(user_to_remove)
    db.commit()
    db.refresh(trip)
    return user_to_remove

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only Trip creator can delete the trip")
    
    db.delete(trip)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{trip_id}/summary", response_model=schemas.TripSummaryResponse)
def trip_summary(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip  = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get all expenses
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()
    total_expense = sum(exp.amount for exp in expenses)
    
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for this trip")
    
    # Get trip members
    members = trip.members
    
    # calculate paid per user
    paid_by_user = {member.id: 0.0 for member in members}
    for exp in expenses:
        if exp.payer_id in paid_by_user:
            paid_by_user[exp.payer_id] += exp.amount
    
    # Equal share
    share_per_user = total_expense / len(members) if members else 0
    
    summary = []
    for member in members:
        paid = round(paid_by_user[member.id],2)
        share = round(share_per_user, 2)
        balance = round(paid - share, 2)
        summary.append(schemas.TripUserSummary(
            user=member.name,
            paid=paid,
            share=share,
            balance=balance
        ))
    
    return schemas.TripSummaryResponse(
        trip_id=trip.id,
        trip_name=trip.name,
        total_expenses=round(total_expense, 2),
        summary=summary
    )
