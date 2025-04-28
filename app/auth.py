from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# JWT settings
SECRET_KEY = 'you never walk alone #ynwa Liverpool'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DB dependecy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User :
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credential_exception
    return user
        

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expiry = datetime.utcnow() + expires_delta
    else:
        expiry = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expiry})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token:str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

