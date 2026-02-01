from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_max_bytes(cls, v: str) -> str:
        try:
            b = v.encode("utf-8")
        except Exception:
            raise ValueError("Неверный формат пароля")
        if len(b) > 72:
            raise ValueError("Пароль слишком длинный: максимум 72 байта (ограничение bcrypt).")
        return v

class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

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

class TaskOut(TaskBase):
    id: int
    status: str
    owner_id: int

    model_config = {"from_attributes": True}

    class Config:
        orm_mode = True
