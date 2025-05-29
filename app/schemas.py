from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode=True

class Token(BaseModel):
    access_token: str
    token_type: str

class TripBase(BaseModel):
    name:str

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    id: int
    creator_id: int

    class Config:
        orm_mode=True

class UserSimple(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class TripDetail(TripResponse):
    members: list[UserSimple] = []

class ExpenseCreate(BaseModel):
    trip_id: int
    title: str
    amount: float
    payer_id: int

class ExpenseResponse(BaseModel):
    id: int
    trip_id: int
    title: str
    amount: float
    payer_id: int
    created_at: datetime
    note: Optional[str] = None

    class Config:
        orm_mode: True

class Settlement(BaseModel):
    from_user: str = Field(..., alias="from")
    to_user: str = Field(..., alias="to")
    amount: float

    class Config:
        allow_population_by_field_name = True

class AddMemberByEmailRequest(BaseModel):
    email: str
    
class RemoveMemeberByEmailRequest(BaseModel):
    email: str

class UpdateExpenseNote(BaseModel):
    note: str
    
class TripUserSummary(BaseModel):
    user: str
    paid: float
    share: float
    balance: float

class TripSummaryResponse(BaseModel):
    trip_id: int
    trip_name: str
    total_expenses: float
    summary: List[TripUserSummary]

