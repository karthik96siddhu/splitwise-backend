from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

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

@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # ensure the current user is the payer
    if expense.payer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this expense")
    
    # Optional : Add trip access check if needed
    
    for key, value in expense_update.dict(exclude_unset=True).items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    return expense

# export expense in csv format
@router.get("/trips/{trip_id}/expenses/breakdown/export")
def export_expense_breakdown_csv(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if current_user not in trip.members and current_user.id != trip.creator_id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this trip's expenses")
    
    results = (
        db.query(
            models.User.name.label("user_name"),
            func.count(models.Expense.id).label("number_of_expenses"),
            func.sum(models.Expense.amount).label("total_amount"),
        )
        .join(models.Expense, models.User.id == models.Expense.payer_id) 
        .filter(models.Expense.trip_id == trip_id)
        .group_by(models.User.id)
        .all()
    )
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['User Name', 'No. of Expenses', 'Total Amount Spent'])
    
    for row in results:
        writer.writerow([row.user_name, row.number_of_expenses, float(row.total_amount or 0)])
    
    output.seek(0)
    
    filename = f"trip_{trip_id}_expenses_breakdown.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )