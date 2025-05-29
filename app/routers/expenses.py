from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Fetch the trip
    trip = db.query(models.Trip).filter(models.Trip.id == expense.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # check if current user is part of the trip
    member_ids = [member.id for member in trip.members]
    if current_user.id not in member_ids:
        raise HTTPException(status_code=403, detail="You are not member of this trip")
    
    # check if payer is the part of the trip
    if expense.payer_id not in member_ids:
        raise HTTPException(status_code=400, detail="Payer is not member of the trip")

    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        trip_id=expense.trip_id,
        payer_id=expense.payer_id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/trip/{trip_id}", response_model=list[schemas.ExpenseResponse])
def get_expenses_for_a_trip(trip_id: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for this trip")
    return expenses

@router.patch("/{expense_id}/note", response_model=schemas.ExpenseResponse)
def update_expense_note(
    expense_id: int,
    request: schemas.UpdateExpenseNote,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # check if current user is the payer
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this expense")
    
    expense.note = request.note
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    trip_id: int,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # prevent deletion if multiple members are involved
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if trip.settled_at is not None:
        raise HTTPException(status_code=400, detail="Cannot delete expense after settlement. Please reset or recalculate settlement first."
    )
    
    expense =db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # check if current user is the payer
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this expense")
    
    db.delete(expense)
    db.commit()
    return 
    