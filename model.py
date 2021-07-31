import uuid
from pydantic import BaseModel, Field


class Todo(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    title: str
    description: str
    completed: bool = False


class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    username: str
    password: str
