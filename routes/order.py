from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Order
from models.user import User
from typing import List
from zeebeClient import client
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

ZEEBE_PROCESS_ID = 'order-management'

orderRouter = APIRouter(prefix='/api/order')


@orderRouter.get('/', response_model=List[Order])
def list_orders(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Listing orders for user_id {user_id}')
    orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
    logger.info(f'Found {len(orders)} orders for user_id {user_id}')
    return orders


@orderRouter.get('/{order_id}', response_model=Order)
def get_order(order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Fetching order with order_id {order_id}')
    order = session.get(Order, order_id)
    if not order:
        logger.warning(f'Order with order_id {order_id} not found')
        raise HTTPException(status_code=404, detail="Order not found")

    logger.info(f'Successfully fetched order with order_id {order_id}')
    return order


@orderRouter.post('/create', response_model=Order)
async def create_order(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(
        f'Creating order for product_id {product_id} by user_id {current_user.id}')
    product = session.get(Product, product_id)
    order = Order(product_id=product_id,
                  user_id=current_user.id, amount=product.price)
    session.add(order)
    session.commit()
    session.refresh(order)

    logger.info(
        f'Starting to run order management process in zeebe for order_id {order.id}')
    process_instance_key = await client.run_process(ZEEBE_PROCESS_ID, variables=order.dict())
    logger.info(
        f'Successfully ran order management process in zeebe for order_id {order.id}, received process_instance_key: {process_instance_key}')

    order.process_instance_key = process_instance_key
    session.commit()
    logger.info(f'Successfully created order with order_id {order.id}')
    return order


@orderRouter.put('/{order_id}', response_model=Order)
async def update_order(order_id: int, status: Optional[str] = None, item_fetched: Optional[int] = None, money_received: Optional[int] = None, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Updating order with order_id {order_id}')
    original_order = session.get(Order, order_id)

    if not original_order:
        logger.warning(f'Order with order_id {order_id} not found')
        raise HTTPException(status_code=404, detail="Order not found")

    if status is not None:
        original_order.status = status

    if item_fetched is not None:
        original_order.item_fetched = item_fetched

    if money_received is not None:
        original_order.money_received = money_received

    session.commit()
    session.refresh(original_order)
    logger.info(f'Successfully updated order with order_id {order_id}')
    return original_order
