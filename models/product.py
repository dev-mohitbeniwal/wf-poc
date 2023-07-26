from sqlmodel import SQLModel, Field
from typing import Optional, List
from models.user import User

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float

class Inventory(SQLModel, table=True):
    product_id: int = Field(default=None, primary_key=True)
    stock_count: int = Field(default=0)

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    amount: float
    process_instance_key: int = None
    item_fetched: int = -1
    money_received: int = -1
    status: str = Field(default="pending")