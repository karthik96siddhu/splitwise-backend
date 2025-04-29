from sqlalchemy.orm import Session
from app import models

def calculate_settlement(trip_id: int, db: Session):
    from collections import defaultdict

    # Get expenses
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()

    # Get users in the trip
    users = (
        db.query(models.User)
        .join(models.trip_members, models.User.id == models.trip_members.c.user_id)
        .filter(models.trip_members.c.trip_id == trip_id)
        .all()
    )

    user_ids = [user.id for user in users]
    user_map = {user.id: user.name for user in users}

    # Calculate total and per person share
    total = sum(exp.amount for exp in expenses)
    share = total / len(users)

    # Calculate net balance for each user
    balances = defaultdict(float)
    for exp in expenses:
        balances[exp.payer_id] += exp.amount

    for uid in user_ids:
        balances[uid] -= share

    # Split into debtors and creditors
    debtors = []
    creditors = []

    for uid, bal in balances.items():
        if round(bal, 2) < 0:
            debtors.append((uid, -bal))  # Needs to pay
        elif round(bal, 2) > 0:
            creditors.append((uid, bal))  # Needs to receive

    # Sort both lists
    debtors.sort(key=lambda x: x[1])
    creditors.sort(key=lambda x: x[1])

    settlements = []

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt = debtors[i]
        creditor_id, credit = creditors[j]

        amount = min(debt, credit)
        settlements.append({
            "from": user_map[debtor_id],
            "to": user_map[creditor_id],
            "amount": round(amount, 2)
        })

        debtors[i] = (debtor_id, debt - amount)
        creditors[j] = (creditor_id, credit - amount)

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
