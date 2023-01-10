from datetime import datetime, timedelta

from jose import JWTError, jwt

SECRET_KEY = "108438820duohdbcnxgtwqotykyug"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    data_to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expire})

    return jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
