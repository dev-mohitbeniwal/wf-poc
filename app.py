import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel
from db import engine
from routes.user import userRouter
from routes.zeebe import zeebeRouter

app = FastAPI(title="Workflow POC")

# Add the routes to the app
app.include_router(userRouter)
app.include_router(zeebeRouter)


origins = [
    'http://localhost:8000',
]

# This is to ensure that following function runs only after all the classes and models have been loaded
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
    uvicorn.run("carsharing:app",  reload=True)