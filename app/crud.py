# app/crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    logger.info("create_user called: email=%s", getattr(user_in, "email", None))
    if not isinstance(user_in.password, str):
        logger.info("password not str")
        raise HTTPException(status_code=400, detail="Invalid password format")

    pw_bytes = user_in.password.encode("utf-8")
    logger.info("password length bytes=%d", len(pw_bytes))

    try:
        hashed = pwd_context.hash(user_in.password)
        logger.info("hashed using schemes: %s", pwd_context.schemes())
    except Exception as e:
        logger.exception("hashing failed: %s", e)
        raise HTTPException(status_code=500, detail="Password hashing failed")

    db_user = models.User(email=user_in.email, hashed_password=hashed, created_at=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("user created id=%s", db_user.id)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    try:
        verified = pwd_context.verify(password, user.hashed_password)
    except Exception:
        return False
    return user if verified else False

def create_task(db: Session, task_in: schemas.TaskCreate, owner_id: int):
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        status=getattr(models, "TaskStatus", None).todo if hasattr(models, "TaskStatus") else "todo",
        due_date=task_in.due_date,
        owner_id=owner_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks_for_user(db: Session, owner_id: int):
    return db.query(models.Task).filter(models.Task.owner_id == owner_id).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_obj: models.Task, task_in: schemas.TaskUpdate):
    if task_in.title is not None:
        task_obj.title = task_in.title
    if task_in.description is not None:
        task_obj.description = task_in.description
    if task_in.status is not None:
        task_obj.status = task_in.status
    if task_in.due_date is not None:
        task_obj.due_date = task_in.due_date
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj

def delete_task(db: Session, task_obj: models.Task):
    db.delete(task_obj)
    db.commit()
