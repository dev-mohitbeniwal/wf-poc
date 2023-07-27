import uvicorn
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.openapi.models import OAuthFlowPassword, OAuthFlows
from sqlmodel import SQLModel
from routes.order import orderRouter
from routes.inventory import inventoryRouter
from routes.product import productRouter
from routes.user import userRouter, meRouter
from db import engine
from utils.logger import setup_logging

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/user/token",
    scopes={"me": "Read information about the current user.",
            "items": "Read items."}
)

setup_logging()
app = FastAPI(title="Workflow POC")

app.openapi().components.security_schemes["OAuth2"] = {
    "type": "oauth2",
    "flows": {
        "password": {
            "tokenUrl": "/api/user/token",
            "scopes": {
                "me": "Read information about the current user.",
                "items": "Read items."
            }
        }
    }
}

# Add the routes to the app
app.include_router(userRouter)
app.include_router(productRouter, tags=["Product"])
app.include_router(orderRouter, tags=["Order"])
app.include_router(inventoryRouter, tags=["Inventory"])
app.include_router(meRouter, tags=["Me"])


origins = [
    'http://localhost:8000',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# This is to ensure that following function runs only after all the classes and models have been loaded


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    uvicorn.run("carsharing:app",  reload=True)
