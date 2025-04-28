from pydantic import BaseModel, EmailStr

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
