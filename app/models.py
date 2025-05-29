from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

trip_members = Table(
    "trip_members",
    Base.metadata,
    Column("trip_id",Integer, ForeignKey("trips.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    trips = relationship("Trip", back_populates="creator")
    joined_trips = relationship("Trip", secondary=trip_members, back_populates="members")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    settled_at = Column(DateTime(timezone=True), nullable=True)

    creator = relationship("User", back_populates="trips")
    members = relationship("User", secondary=trip_members, back_populates="joined_trips")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    # here we used ondelete="CASCADE". It means if trip deleted, its expenses also deleted.
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    # ondelete="SET NULL". It means if user is deleted, there expenses stays but payer_id becomes NULL.
    payer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    note = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


