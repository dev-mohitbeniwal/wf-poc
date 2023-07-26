import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from db import engine
from routes.user import userRouter
from routes.zeebe import zeebeRouter
from routes.product import productRouter, orderRouter, inventoryRouter

app = FastAPI(title="Workflow POC")

# Add the routes to the app
app.include_router(userRouter)
app.include_router(zeebeRouter)
app.include_router(productRouter, tags=["Product"])
app.include_router(orderRouter, tags=["Order"])
app.include_router(inventoryRouter, tags=["Inventory"])


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