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

productRouter = APIRouter(prefix='/api/product')
inventoryRouter = APIRouter(prefix='/api/inventory')
orderRouter = APIRouter(prefix='/api/order')


@productRouter.get('/{product_id}', response_model=Product)
def get_product(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print("Inside get_product")
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@productRouter.get('/', response_model=List[Product])
def list_products(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    print('Inside list_products')
    products = session.exec(select(Product)).all()
    return products


@productRouter.post('/', response_model=Product)
def create_product(product: Product, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # product = Product(name=name, price=price, description=description)
    print('Inside create_product')
    session.add(product)
    session.commit()
    session.refresh(product)

    inventory = Inventory(product_id=product.id, stock_count=0)
    session.add(inventory)
    session.commit()

    return product


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
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inventory = session.get(Inventory, product_id)
    if not inventory:
        inventory = Inventory(product_id=product_id, stock_count=stock_count)
        session.add(inventory)
    else:
        inventory.stock_count = stock_count

    session.commit()
    session.refresh(inventory)
    return inventory


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
