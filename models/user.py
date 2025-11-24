from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

class User(UserBase):
    id: int
