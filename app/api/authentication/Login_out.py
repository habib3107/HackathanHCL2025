from fastapi import APIRouter,Depends,HTTPException,status,Request,Form
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.login_user import LoginUser

from app.core.security import verify_password,create_access_token
from datetime import datetime,timedelta
from app.core.security import get_current_user,decode_jwt
from jose import JWTError
import pytz
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")
router=APIRouter()

class OAuth2PasswordRequestFormWithRemember(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        remember_me: bool = Form(False)  
    ):
        super().__init__(username=username, password=password, scope=scope, client_id=client_id, client_secret=client_secret)
        self.remember_me = remember_me

@router.post(
        "/login",
        responses={
            200: {"description": "Login successful. Returns access token."},
            400: {"description": "Bad Request - Invalid input or missing fields"},
            401: {"description": "Unauthorized - Invalid email or password"},
            500: {"description": "Internal Server Error - Login failed"},
    }            
)
def login(
    request: OAuth2PasswordRequestFormWithRemember = Depends(),
    db: Session = Depends(get_db),
 
):
    try:
        user = db.query(LoginUser).filter(LoginUser.email == request.username).first()

        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(days=30) if request.remember_me else timedelta(hours=1)
        user.last_activity = datetime.now()
        db.commit()

        access_token = create_access_token(data={"sub": request.username,"role":user.role,"user_id":user.user_id,"name":user.First_name},expries_delta=access_token_expires)

        return {
            "user_id":user.user_id,
            "name":user.First_name,
            "role":user.role,
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during login. Please try again later.")



@router.post(
        "/logout",
        responses={
        200: {"description": "Successfully logged out and token blacklisted."},
        400: {"description": "Bad Request - Token already invalidated or inactive user."},
        401: {"description": "Unauthorized - Invalid token."},
        500: {"description": "Internal Server Error - Logout failed."}
    }
)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        
        token_data = decode_jwt(token)
        now_user = db.query(LoginUser).filter(LoginUser.email == token_data["sub"]).first()

        if now_user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is valid but no matching user found.")

        if now_user.last_activity and abs(datetime.now() - now_user.last_activity) > timedelta(days=1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has been inactive for more than one day.")

        

        exp = token_data.get("exp")
        expires_at_utc = datetime.utcfromtimestamp(exp).replace(tzinfo=pytz.UTC)

        ist = pytz.timezone("Asia/Kolkata")
        expires_at_ist = expires_at_utc.astimezone(ist)

        now_ist = datetime.now(ist)
        time_remaining = expires_at_ist - now_ist
        return {
            "message": "SuccessFully logged out",
            "Expires": expires_at_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "you_logout_before": str(time_remaining)
        }

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An unexpected error occurred during logout. Please try again later.")


@router.get(
        "/user-test",
        responses={
        200: {"description": "Current user data retrieved successfully"},
        500: {"description": "Internal Server Error while retrieving user"},
    }
)
def check_user(
    current_user: LoginUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        current_user.last_activity = datetime.utcnow()
        db.commit()
        return {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name":current_user.First_name,
            "role":current_user.role
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving user: {str(e)}")


