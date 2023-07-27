from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Inventory
from models.user import User
from typing import List

inventoryRouter = APIRouter(prefix='/api/inventory')

@inventoryRouter.get('/', response_model=List[Inventory])
def list_inventory(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print('Inside list_inventory')
    inventory = session.exec(select(Inventory)).all()
    return inventory


@inventoryRouter.get('/{product_id}', response_model=Inventory)
def get_inventory(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print("Inside get_inventory")
    inventory = session.get(Inventory, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return inventory


@inventoryRouter.put('/{product_id}', response_model=Inventory)
def update_inventory(product_id: int, stock_count: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print("Inside update_inventory")
    inventory = session.get(Inventory, product_id)
    if not inventory:
        inventory = Inventory(product_id=product_id, stock_count=stock_count)
        session.add(inventory)
    else:
        inventory.stock_count = stock_count

    session.commit()
    session.refresh(inventory)
    return inventory