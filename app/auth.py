from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
from . import models
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=8)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        u_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == u_id).first()
    if user is None:
        raise credentials_exception
    return user
