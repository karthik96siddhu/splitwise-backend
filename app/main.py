from fastapi import FastAPI
from app.routers import users
from app.database import engine, Base

# create db tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routes
app.include_router(users.router)
