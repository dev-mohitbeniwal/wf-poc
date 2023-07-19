from jose import jwt, JWTError
from pydantic import ValidationError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import Optional

from models.user import User
from db import get_session

SECRET_KEY="test_secret_key"
ALGORITHM="HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    crendentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise crendentials_exception
    except (JWTError, ValidationError):
        raise crendentials_exception

    user = db.query(User).where(User.username == username).first()
    if user is None:
        raise crendentials_exception

    return user