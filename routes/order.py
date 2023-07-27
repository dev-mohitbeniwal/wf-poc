from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Inventory, Order
from models.user import User
from typing import List
from zeebeClient import client
from typing import Optional


ZEEBE_PROCESS_ID = 'order-management'

orderRouter = APIRouter(prefix='/api/order')

@orderRouter.get('/', response_model=List[Order])
def list_orders(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print('Inside list_orders')
    print(current_user, 'Inside list_orders')
    orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
    # orders = session.exec(select(Order)).all()
    return orders


@orderRouter.get('/{order_id}', response_model=Order)
def get_order(order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print("Inside get_order")
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@orderRouter.post('/create', response_model=Order)
async def create_order(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    order = Order(product_id=product_id,
                  user_id=current_user.id, amount=product.price)
    session.add(order)
    session.commit()
    session.refresh(order)
    process_instance_key = await client.run_process(ZEEBE_PROCESS_ID, variables=order.dict())
    order.process_instance_key = process_instance_key
    session.commit()
    return order


@orderRouter.put('/{order_id}', response_model=Order)
async def update_order(order_id: int, status: Optional[str] = None, item_fetched: Optional[int] = None, money_received: Optional[int] = None, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print('Inside update_order')
    original_order = session.get(Order, order_id)

    if not original_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status is not None:
        original_order.status = status

    if item_fetched is not None:
        original_order.item_fetched = item_fetched

    if money_received is not None:
        original_order.money_received = money_received

    session.commit()
    session.refresh(original_order)

    return original_order
