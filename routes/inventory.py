from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Inventory
from models.user import User
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)

inventoryRouter = APIRouter(prefix='/api/inventory')


@inventoryRouter.get('/', response_model=List[Inventory])
def list_inventory(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info('Fetching all inventory')
    inventory = session.exec(select(Inventory)).all()
    logger.info(f'Fetched {len(inventory)} inventory items')
    return inventory


@inventoryRouter.get('/{product_id}', response_model=Inventory)
def get_inventory(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Fetching inventory for product id {product_id}')
    inventory = session.get(Inventory, product_id)
    if not inventory:
        logger.warning(f'No inventory found for product id {product_id}')
        raise HTTPException(status_code=404, detail="Inventory not found")

    logger.info(f'Fetched inventory for product id {product_id}')
    return inventory


@inventoryRouter.put('/{product_id}', response_model=Inventory)
def update_inventory(product_id: int, stock_count: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Updating inventory for product id {product_id}')
    inventory = session.get(Inventory, product_id)
    if not inventory:
        inventory = Inventory(product_id=product_id, stock_count=stock_count)
        session.add(inventory)
        logger.info(f'Created new inventory for product id {product_id}')
    else:
        inventory.stock_count = stock_count
        logger.info(f'Updated inventory for product id {product_id}')

    session.commit()
    session.refresh(inventory)
    return inventory
