from typing import Optional
from datetime import datetime

import pydantic
from pydantic import BaseModel, EmailStr, validator

_PYDANTIC_VER = getattr(pydantic, "__version__", "1.0.0")
_PYDANTIC_MAJOR = int(_PYDANTIC_VER.split(".")[0])
IS_PYDANTIC_V2 = _PYDANTIC_MAJOR >= 2


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_max_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")
        return v


if IS_PYDANTIC_V2:
    class UserOut(UserBase):
        id: int
        created_at: datetime

        model_config = {"from_attributes": True}
else:
    class UserOut(UserBase):
        id: int
        created_at: datetime

        class Config:
            orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None


if IS_PYDANTIC_V2:
    class TaskOut(TaskBase):
        id: int
        status: str
        owner_id: int

        model_config = {"from_attributes": True}
else:
    class TaskOut(TaskBase):
        id: int
        status: str
        owner_id: int

        class Config:
            orm_mode = True
