from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        email=user_in.email,
        hashed_password=pwd_context.hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_task(db: Session, task_in: schemas.TaskCreate, owner_id: int) -> models.Task:
    task = models.Task(**task_in.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks_for_user(
    db: Session,
    owner_id: int,
    status: Optional[str] = None,
    priority: Optional[int] = None,
) -> list[models.Task]:
    query = db.query(models.Task).filter(models.Task.owner_id == owner_id)
    if status is not None:
        query = query.filter(models.Task.status == status)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    return query.all()


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task: models.Task, task_in: schemas.TaskUpdate) -> models.Task:
    for field, value in task_in.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    db.delete(task)
    db.commit()
