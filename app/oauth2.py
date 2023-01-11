from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from . import schemas

oauth2_scheme = OAuth2PasswordBearer("login")

SECRET_KEY = "108438820duohdbcnxgtwqotykyug"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    data_to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expire})

    return jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)
