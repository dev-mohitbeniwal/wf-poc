from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from utils.auth import get_current_user
from models.product import Product, Inventory
from models.user import User
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)

productRouter = APIRouter(prefix='/api/product')


@productRouter.get('/{product_id}', response_model=Product)
def get_product(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Fetching product with product_id {product_id}')
    product = session.get(Product, product_id)
    if not product:
        logger.warning(f'Product with product_id {product_id} not found')
        raise HTTPException(status_code=404, detail="Product not found")

    logger.info(f'Successfully fetched product with product_id {product_id}')
    return product


@productRouter.get('/', response_model=List[Product])
def list_products(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info('Listing all products')
    products = session.exec(select(Product)).all()
    logger.info(f'Found {len(products)} products')
    return products


@productRouter.post('/', response_model=Product)
def create_product(product: Product, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f'Creating new product with name {product.name}')
    session.add(product)
    session.commit()
    session.refresh(product)

    inventory = Inventory(product_id=product.id, stock_count=0)
    session.add(inventory)
    session.commit()

    logger.info(f'Successfully created product with product_id {product.id}')
    return product
