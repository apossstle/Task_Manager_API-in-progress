from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

from . import models, schemas, crud, database, auth

app = FastAPI(title="Task Manager API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend")), name="static")


def get_task_or_404(task_id: int, current_user: models.User, db: Session) -> models.Task:
    task = crud.get_task(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/tasks-page", response_class=HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/users/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user_in)


@app.post("/users/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": auth.create_access_token({"sub": str(user.id)}), "token_type": "bearer"}


@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    return crud.create_task(db, task_in, current_user.id)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=3),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    return crud.get_tasks_for_user(db, current_user.id, status=status, priority=priority)


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    return get_task_or_404(task_id, current_user, db)


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    task = get_task_or_404(task_id, current_user, db)
    return crud.update_task(db, task, task_in)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    task = get_task_or_404(task_id, current_user, db)
    crud.delete_task(db, task)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
