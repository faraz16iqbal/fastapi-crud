from fastapi.param_functions import Depends
from pydantic.networks import AnyUrl
from starlette.status import HTTP_200_OK
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, HTTPException, Request, status
from model import User
from auth import AuthHandler
import sys
sys.path.append("..")

router = APIRouter()
auth_handler = AuthHandler()


@router.post("/register", response_model=User, response_description="Register a user")
async def register_user(request: Request, user: User):
    user = jsonable_encoder(user)
    existing_user = await request.app.mongodb["user"].find_one(
        {"username": user['username']})
    if(existing_user is not None):
        raise HTTPException(409, "User with same username already exists")
    hashed_password = auth_handler.get_pass_hash(user['password'])
    user['password'] = hashed_password
    new_user = await request.app.mongodb["user"].insert_one(user)
    created_user = await request.app.mongodb['user'].find_one({
        "_id": new_user.inserted_id  # mongo db returns inserted id and not the object
    })
    if(created_user):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)
    raise HTTPException(400, "Something went wrong")


@router.post("/login", response_model=User, response_description="Login user")
async def login_user(request: Request, user: User):
    user = jsonable_encoder(user)
    existing_user = await request.app.mongodb["user"].find_one(
        {"username": user["username"]})

    if(existing_user is None) or (not auth_handler.verify_password(user['password'], existing_user['password'])):
        raise HTTPException(401, "Invalid username/password")
    print(user["_id"])
    token = auth_handler.encode_token(user["_id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})


@router.get("/", response_description="Get all users")
async def get_users(request: Request):
    users = []
    for doc in await request.app.mongodb["user"].find().to_list(100):
        users.append(doc)
    return users


@router.get("/protected")
def protected(id=Depends(auth_handler.auth_wrapper)):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"id": id})
