from model import Todo
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

import sys
sys.path.append("..")

router = APIRouter()


@router.post("/", response_model=Todo, response_description="Add a todo")
async def post_todo(request: Request, todo: Todo):
    todo = jsonable_encoder(todo)
    new_task = await request.app.mongodb["TodoList"].insert_one(todo)
    created_task = await request.app.mongodb['TodoList'].find_one({
        "_id": new_task.inserted_id  # mongo db returns inserted id and not the object
    })
    if(new_task):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_task)
    raise HTTPException(400, "Something went wrong")


@router.get("/", response_description="Get all todos")
async def get_todo(request: Request):
    tasks = []
    for doc in await request.app.mongodb["TodoList"].find().to_list(100):
        tasks.append(doc)
    return tasks


@router.get("/{id}", response_model=Todo, response_description="Get todo by ID")
async def get_todo_by_title(id: str, request: Request):
    task = await request.app.mongodb["TodoList"].find_one({"_id": id})
    if(task is not None):
        return task
    raise HTTPException(404, f"There is no todo with the id {id}")


@router.put("/{id}", response_model=Todo, response_description="Update todo by ID")
async def put_todo(id: str, request: Request, todo: Todo):

    existing_task = await request.app.mongodb["TodoList"].find_one({"_id": id})
    if(existing_task is None):
        raise HTTPException(404, f"There is no todo with the title {id}")

    await request.app.mongodb["TodoList"].update_one({"_id": id}, {"$set": {
        "title": todo.title or existing_task.title,
        "description": todo.description or existing_task.description,
        "completed": todo.completed or existing_task.completed
    }})

    task = await request.app.mongodb["TodoList"].find_one({"_id": id})
    if(task is not None):
        return task


@router.delete("/{id}", response_description="Delete todo by ID")
async def remove_todo(id: str, request: Request):
    delete_result = await request.app.mongodb["TodoList"].delete_one({"_id": id})
    if(delete_result.deleted_count == 1):
        return JSONResponse(status_code=HTTP_200_OK, content="Todo deleted succesfully!")
    raise HTTPException(404, f"Todo with {id} not found")
