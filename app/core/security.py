from passlib.context import CryptContext
from datetime import timedelta,datetime
from app.core.config import settings
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status,Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.login_user import LoginUser


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
blackedlist_token=set()

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict,expries_delta:timedelta=None):
    to_encode=data.copy()
    expries_time=datetime.utcnow()+(expries_delta if expries_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expries_time})
    encrypt=jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encrypt

def create_reset_token(email:str) -> str:
    expire=datetime.now()+timedelta(minutes=10)
    payload={
        "sub":email,
        "exp":expire,
        "scope":"reset_password"
    }

    token=jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token
def decode_jwt(token:str):
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id= payload.get("user_id")

        if not email or not role or not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(LoginUser).filter(LoginUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# def allow_roles(*allowed_roles: RoleChoose):
#     def dependency(current_user=Depends(get_current_user)):
#         if current_user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Access denied. Required roles: {allowed_roles}"
#             )
#         return current_user
#     return dependency