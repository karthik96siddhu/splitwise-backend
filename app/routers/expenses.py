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

@router.get("/trip/{trip_id}/split")
def split_expenses(trip_id: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for this trip")
    
    # 1. Calcultae total amount
    total_amount = sum(exp.amount for exp in expenses)

    #2. Find unique users who paid.
    user_ids = set(exp.payer_id for exp in expenses)
    num_users = len(user_ids)

    if num_users == 0:
        raise HTTPException(status_code=400, details="No particpants to split among")
    
    # 3. Equal shares
    share_per_user = total_amount/num_users

    # 4. Calculate amount paid by each user
    paid_by_user = {}
    for exp in expenses:
        paid_by_user[exp.payer_id] = paid_by_user.get(exp.payer_id, 0) + exp.amount

    # 5. Calculate net balance
    balances = {}
    for user_id in user_ids:
        paid = paid_by_user.get(user_id, 0)
        balances[user_id] = round(paid - share_per_user, 2)
    
    return {
        "total_amount": total_amount,
        "share_per_user": round(share_per_user, 2),
        "balances": balances
    }
