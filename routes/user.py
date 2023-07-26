from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from db import get_session
from models.user import User, UserCreate, UserRead, Token, UserBase
from datetime import timedelta, datetime
from typing import Optional
from utils.auth import SECRET_KEY, ALGORITHM, get_current_user

ACCESS_TOKEN_EXPIRE_MINUTES=900

userRouter = APIRouter(prefix="/api/user")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoint to register a new user
@userRouter.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_session)):
    print('inside register user')
    # Check if the username already exists
    query = select(User).where(User.username == user.username)
    if db.exec(query).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create a new user isntance and set the password with encryption
    db_user = User.create(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Endpoint to update the user
@userRouter.put("/", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_self(balance: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    print('inside update self')
    user = db.get(User, current_user.id)
    if (not user):
        raise HTTPException(status_code=400, detail="User not found")
    user.balance = balance
    db.commit()
    return user

# Endpoint to update the user
@userRouter.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(user_id: int, balance: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    print('inside update user')
    user = db.get(User, user_id)
    if (not user):
        raise HTTPException(status_code=400, detail="User not found")
    user.balance = balance
    db.commit()
    return user


@userRouter.post("/login")
def login(username: str, password: str, db: Session = Depends(get_session)):
    print('inside login')
    user = db.query(User).where(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"message": "Logged in successfully"}


@userRouter.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    print('inside token')
    user = db.query(User).where(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expiers = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "name": user.name, "department": user.department, "id": user.id, "email": user.email }, expires_delta=access_token_expiers
    )

    return {"access_token": access_token, "token_type": "bearer"}

@userRouter.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_session)):
    print('inside read user')
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.get("/me")
def read_users_me(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print('inside read users me')
    user = session.get(User, current_user.id)
    return user