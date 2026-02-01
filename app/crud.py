from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    pw_bytes = user_in.password.encode('utf-8') if isinstance(user_in.password, str) else bytes(user_in.password)
    if len(pw_bytes) > 72:
        raise HTTPException(status_code=400,
                            detail="Password too long: bcrypt supports up to 72 bytes. Use a shorter password.")
    hashed = pwd_context.hash(user_in.password)
    db_user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_task(db: Session, task_in: schemas.TaskCreate, owner_id: int):
    task = models.Task(title=task_in.title, description=task_in.description, owner_id=owner_id)
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
