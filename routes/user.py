from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select
from db import get_session
from models.user import User, UserCreate, UserRead, Token
from datetime import timedelta, datetime
from typing import Optional
from utils.auth import SECRET_KEY, ALGORITHM, get_current_user

DEFAULT_EXPIRATION=timedelta(minutes=900)

userRouter = APIRouter(prefix='/api/user')
meRouter = APIRouter(prefix='/api/me')

@userRouter.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.create(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@userRouter.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, balance: float, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance = balance
    session.commit()
    session.refresh(user)
    return user

@userRouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    if not user.verify_password(form_data.password):
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    access_token_expires = DEFAULT_EXPIRATION
    token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + access_token_expires,
        "email": user.email,
        "department": user.department,
        "name": user.name,
        "balance": user.balance
    }
    access_token = Token(access_token=jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM), token_type="bearer")
    return access_token

@meRouter.get("/", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@meRouter.put("/", response_model=UserRead)
def update_users_me(balance: float, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    current_user.balance = balance
    session.commit()
    session.refresh(current_user)
    return current_user
