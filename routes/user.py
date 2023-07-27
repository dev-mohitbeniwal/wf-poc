from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select
from db import get_session
from models.user import User, UserCreate, UserRead, Token
from datetime import timedelta, datetime
from typing import Optional
from utils.auth import SECRET_KEY, ALGORITHM, get_current_user
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_EXPIRATION = timedelta(minutes=900)

userRouter = APIRouter(prefix='/api/user')
meRouter = APIRouter(prefix='/api/me')


@userRouter.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    logger.info(f'Creating new user with username {user.username}')
    db_user = User.create(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.info(f'Successfully created user with user_id {db_user.id}')
    return db_user


@userRouter.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Fetching user with user_id {user_id}')
    user = session.get(User, user_id)
    if not user:
        logger.warning(f'User with user_id {user_id} not found')
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f'Successfully fetched user with user_id {user_id}')
    return user


@userRouter.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, balance: float, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Updating balance for user_id {user_id}')
    user = session.get(User, user_id)
    if not user:
        logger.warning(f'User with user_id {user_id} not found')
        raise HTTPException(status_code=404, detail="User not found")

    user.balance = balance
    session.commit()
    session.refresh(user)
    logger.info(f'Successfully updated balance for user_id {user_id}')
    return user


@userRouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    logger.info(f'Attempting login for username {form_data.username}')
    user = session.exec(select(User).where(
        User.username == form_data.username)).first()
    if not user or not user.verify_password(form_data.password):
        logger.warning(
            f'Incorrect username or password for username {form_data.username}')
        raise HTTPException(
            status_code=404, detail="Incorrect username or password")

    access_token_expires = DEFAULT_EXPIRATION
    token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + access_token_expires,
        "email": user.email,
        "department": user.department,
        "name": user.name,
        "balance": user.balance
    }

    access_token = Token(access_token=jwt.encode(
        token_data, SECRET_KEY, algorithm=ALGORITHM), token_type="bearer")
    logger.info(f'Successfully logged in username {form_data.username}')
    return access_token


@meRouter.get("/", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    logger.info(
        f'Fetching details for the logged-in user with user_id {current_user.id}')
    return current_user


@meRouter.put("/", response_model=UserRead)
def update_users_me(balance: float, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(
        f'Updating balance for the logged-in user with user_id {current_user.id}')
    current_user.balance = balance
    session.commit()
    session.refresh(current_user)
    logger.info(
        f'Successfully updated balance for the logged-in user with user_id {current_user.id}')
    return current_user
