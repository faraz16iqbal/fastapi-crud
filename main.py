from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from fastapi import FastAPI, HTTPException

import routers.todo as todo_router
import routers.user as user_router

app = FastAPI()


@app.on_event("startup")
async def start_up_client():
    app.mongodb_client = AsyncIOMotorClient('mongodb://localhost:27017')
    app.mongodb = app.mongodb_client['TodoList']


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

origins = [
    "http://localhost:3000",
]

# what is a middleware?
# software that acts as a bridge between an operating system or database and applications, especially on a network.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return "FastAPI server is up and running"

app.include_router(todo_router.router, tags=["todo"], prefix="/todo")
app.include_router(user_router.router, tags=["user"], prefix="/user")


if(__name__ == '__main__'):
    uvicorn.run(
        "main:app",
        reload=True,
        port=8000
    )
