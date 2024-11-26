from datetime import datetime, timedelta

from argon2 import PasswordHasher
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from config import ALGORITHM, SECRET_KEY
from src.handlers.client import Client


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    is_admin: bool = False


class TokenData(BaseModel):
    username: str | None = None


def get_token_header(token: str = Header(alias="Authorization", default="")):
    return token


hasher = PasswordHasher()


def verify_password(plain_password, hashed_password):
    try:
        return hasher.verify(hashed_password, plain_password)
    except:
        return False


def hash_password(password):
    return hasher.hash(password)


async def get_user(username: str):
    return await Client.init(
        client=username, username=username, get_by_username=True, pre_register=False
    )


async def authenticate_user(username: str, password: str):
    user = await get_user(username)

    if not user:
        raise HTTPException(status_code=401)

    if not user.password:
        return False

    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(get_token_header)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        iss: str = payload.get("iss")

        if iss != "access_token":
            raise credentials_exception

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = await get_user(token_data.username)

    if user is None:
        raise credentials_exception

    if user.is_dev and "admin" not in payload.get("scopes", []):
        raise credentials_exception

    return user


async def admin_resource(user: Client = Depends(get_current_user)):
    if not user.is_dev:
        raise HTTPException(status_code=403, detail="Forbidden")

    return user


class Login(BaseModel):
    username: str
    password: str
