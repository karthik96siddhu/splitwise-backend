from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_user_by_email(db: Session, email:str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db:Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        name=user.name, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_trip(db: Session, trip: schemas.TripCreate, user_id: int):
    db_trip = models.Trip(name=trip.name, creator_id=user_id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def add_member_to_trip(db: Session, trip_id: int, user_id: int):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not trip or not user:
        return None
    
    trip.members.append(user)
    db.commit()
    db.refresh(trip)
    return trip


