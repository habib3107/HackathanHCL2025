
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.login_user import LoginUser
from app.core.security import hash_password
from datetime import datetime, date
from enum import Enum
from app.function.generating_id import generate_user_code
from app.function.validation import validate_email, validate_phone_number
from app.core.security import get_current_user

router = APIRouter()

class SignroleupRequestForm(str, Enum):
    customer = "Customer"
    
class AdminroleupRequestForm(str, Enum):
    Admin = "Admin"
    Auditor = "Auditor"
    superadmin = "superadmin"
    
class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

    
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(None),
    last_name: str = Form(None),
    gender: GenderEnum= Form(None),
    dob: date = Form(None),
    role: SignroleupRequestForm = Form(...),
    db: Session = Depends(get_db)
):
    # Check existing user by email or phone
    existing_user = db.query(LoginUser).filter(
        (LoginUser.email == email) | (LoginUser.phone_number == phone_number)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email or phone number."
        )
    # Validate email and phone number
    validate_email(email)
    validate_phone_number(phone_number)

    # Hash the password
    hashed_pw = hash_password(password)
    
    # Generate unique user ID
    user_id = generate_user_code(db, role)
    # Create new user entry
    new_user = LoginUser(
        user_id=user_id,
        username=username,
        email=email,
        phone_number=phone_number,
        password=password,  # raw password (optional to store)
        hashed_password=hashed_pw,
        First_name=first_name,
        Last_name=last_name,
        Gender=gender,
        DOB=dob,
        role=role.value,
        
    ) 

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User registered successfully.",
        "data": {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "role": new_user.role
        }
    }


@router.post("/admin-signup", status_code=status.HTTP_201_CREATED)
def admin_signup(
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(None),
    last_name: str = Form(None),
    gender: GenderEnum= Form(None),
    dob: date = Form(None),
    role: AdminroleupRequestForm = Form(...),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Check existing user by email or phone
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. only superadmin allowed"
        )
    existing_user = db.query(LoginUser).filter(
        (LoginUser.email == email) | (LoginUser.phone_number == phone_number)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email or phone number."
        )
    # Validate email and phone number
    validate_email(email)
    validate_phone_number(phone_number)

    # Hash the password
    hashed_pw = hash_password(password)
    
    # Generate unique user ID
    user_id = generate_user_code(db, role)
    # Create new user entry
    new_user = LoginUser(
        user_id=user_id,
        username=username,
        email=email,
        phone_number=phone_number,
        password=password,  # raw password (optional to store)
        hashed_password=hashed_pw,
        First_name=first_name,
        Last_name=last_name,
        Gender=gender,
        DOB=dob,
        role=role.value,
        
    ) 

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User registered successfully.",
        "data": {
            "user_id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "role": new_user.role
        }
    }
@router.get("/get_users", status_code=status.HTTP_200_OK)
def get_users(
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
    
):
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. only superadmin allowed"
        )
    users = db.query(LoginUser).all()
    return {
        "status": "success",
        
        "users": [
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "status": user.status
                } for user in users
            ]
        
    }
    
    
@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    user_id: str,
    username: str = Form(None),
    email: str = Form(None),
    phone_number: str = Form(None),
    password: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    gender: str = Form(None),
    dob: date = Form(None),
    role: str = Form(None),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. only superadmin allowed"
        )
    user = db.query(LoginUser).filter(LoginUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Validate if email or phone already exists for another user
    if email:
        validate_email(email)
        existing_email = db.query(LoginUser).filter(
            LoginUser.email == email, LoginUser.user_id != user_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already in use by another user.")
        user.email = email

    if phone_number:
        validate_phone_number(phone_number)
        existing_phone = db.query(LoginUser).filter(
            LoginUser.phone_number == phone_number, LoginUser.user_id != user_id
        ).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already in use by another user.")
        user.phone_number = phone_number

    # Update remaining fields if provided
    if username: user.username = username
    if first_name: user.First_name = first_name
    if last_name: user.Last_name = last_name
    if gender: user.Gender = gender
    if dob: user.DOB = dob
    if role: user.role = role

    if password:
        user.password = password
        user.hashed_password = hash_password(password)

    user.updated_at = datetime.now()

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "User updated successfully.",
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        },
    }

# -------------------------------
# 🔴 DELETE USER (DELETE)
# -------------------------------
@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. only superadmin allowed"
        )
    user = db.query(LoginUser).filter(LoginUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(user)
    db.commit()

    return {
        "status": "success",
        "message": f"User with ID {user_id} deleted successfully."
    }