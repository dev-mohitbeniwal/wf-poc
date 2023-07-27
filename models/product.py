from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.user import User
from datetime import datetime

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    inventory: Optional["Inventory"] = Relationship(back_populates="product")
    orders: Optional[List["Order"]] = Relationship(back_populates="product")

class Inventory(SQLModel, table=True):
    product_id: int = Field(default=None, primary_key=True)
    stock_count: int = Field(default=0)
    product: Optional[Product] = Relationship(back_populates="inventory")

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    amount: float
    process_instance_key: int = None
    item_fetched: int = -1
    money_received: int = -1
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    product: Optional[Product] = Relationship(back_populates="orders")
    user: Optional[User] = Relationship(back_populates="orders")
    timestamp: datetime = Field(default=datetime.utcnow())