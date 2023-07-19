from sqlmodel import SQLModel, Field
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

# Password encryption context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(SQLModel):
    username: str
    name: str
    department: str
    age: int
    balance: float

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    @classmethod
    def create(cls, user: UserCreate):
        user.password = pwd_context.hash(user.password)
        db_user = cls(**user.dict())
        return db_user
    

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

