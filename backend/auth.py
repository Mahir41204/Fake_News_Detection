from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, Any, Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def register_user(
    session: AsyncSession, email: str, password: str
) -> Tuple[Optional[User], Optional[str]]:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return None, "Email already registered."
    hashed_pw = hash_password(password)
    new_user = User(email=email, hashed_password=hashed_pw)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user, None


async def login_user(
    session: AsyncSession, email: str, password: str
) -> Tuple[Optional[str], Optional[str]]:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, str(user.hashed_password)):
        return None, "Invalid email or password."
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return token, None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("sub")
        if user_id is None or email is None:
            raise credentials_exception
        return {"user_id": user_id, "email": email}
    except JWTError:
        raise credentials_exception
