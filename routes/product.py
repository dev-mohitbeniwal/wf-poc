from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Inventory
from models.user import User
from typing import List

productRouter = APIRouter(prefix='/api/product')

@productRouter.get('/{product_id}', response_model=Product)
def get_product(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@productRouter.get('/', response_model=List[Product])
def list_products(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products


@productRouter.post('/', response_model=Product)
def create_product(product: Product, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)

    inventory = Inventory(product_id=product.id, stock_count=0)
    session.add(inventory)
    session.commit()

    return product
