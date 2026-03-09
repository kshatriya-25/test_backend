from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def create_access_token(data: dict):
    
    paylaod = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    paylaod.update({
        "exp" : expire
    })

    token = jwt.encode(
        paylaod,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_pswd(password: str):
    return pwd_context.hash(password)

def verify_pswd(password : str , hashed_password: str):
    return pwd_context.verify(password , hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"id": int(user_id), "role": payload.get("role")}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")