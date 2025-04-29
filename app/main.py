from fastapi import FastAPI
from app.routers import users, trips, expenses
from app.database import engine, Base

# create db tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routes
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(expenses.router)