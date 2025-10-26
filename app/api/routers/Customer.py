from fastapi import APIRouter, Form, Depends, HTTPException, status,UploadFile, File,Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.models.login_user import LoginUser
from app.function.validation import validate_email, validate_phone_number
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.CustomerModel import Customer
from app.function.generating_id import generate_Customer_code
import os
from fastapi.responses import FileResponse
from enum import Enum
from app.enumsfolder.CustomerEnum import GenderEnum, MaritalStatusEnum,AccountTypeEnum
router = APIRouter()
UPLOAD_DIR = "uploads/customers/"

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_customer(
    first_name: str = Form(...),
    last_name: str = Form(None),
    date_of_birth: date = Form(...),
    gender: GenderEnum = Form(...),
    marital_status: MaritalStatusEnum = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    alternate_phone: str = Form(None),
    address_line1: str = Form(...),
    address_line2: str = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    country: str = Form(...),
    postal_code: str = Form(...),
    account_type: AccountTypeEnum = Form(...),
    occupation: str = Form(None),
    annual_income: str = Form(None),
    profile_photo: UploadFile = File(None),
    signature_image: UploadFile = File(None),

    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. only Customer care allowed"
        )
    # 🔹 Validate email and phone
    validate_email(email)
    validate_phone_number(phone_number)

    # 🔹 Check for duplicates
    existing_customer = db.query(Customer).filter(
        (Customer.email == email) | (Customer.phone_number == phone_number)
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already exists with this email or phone number."
        )
        
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    customer_code = generate_Customer_code(db)
    
    profile_path = None
    signature_path = None

    if profile_photo:
        file_ext = os.path.splitext(profile_photo.filename)[1]  # get extension
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        safe_filename = profile_photo.filename.replace(" ", "_")  # optional: remove spaces
        profile_path = os.path.join(
            UPLOAD_DIR,
            f"{customer_code}_profile_{timestamp}{file_ext}"
        )
        with open(profile_path, "wb") as f:
            f.write(await profile_photo.read())

    if signature_image:
        file_ext = os.path.splitext(signature_image.filename)[1]
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        safe_filename = signature_image.filename.replace(" ", "_")
        signature_path = os.path.join(
            UPLOAD_DIR,
            f"{customer_code}_signature_{timestamp}{file_ext}"
        )
        with open(signature_path, "wb") as f:
            f.write(await signature_image.read())

    # 🔹 Generate a unique customer code
    
    

    # 🔹 Create new customer
    new_customer = Customer(
        customer_code=customer_code,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender.value,
        marital_status=marital_status.value,
        email=email,
        phone_number=phone_number,
        alternate_phone=alternate_phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code,
        account_type=account_type.value,
        occupation=occupation,
        annual_income=annual_income,
        notes=notes,
        profile_photo=profile_path,
        signature_image=signature_path,
        login_id=current_user.user_table_id
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "status": "success",
        "message": "Customer created successfully.",
        "data": {
            "customer_code": new_customer.customer_code,
            "name": f"{new_customer.first_name} {new_customer.last_name or ''}".strip(),
            "email": new_customer.email,
            "phone_number": new_customer.phone_number,
            "account_type": new_customer.account_type,
            "status": new_customer.status,
        }
    }
    
@router.get("/get-all-customer", status_code=status.HTTP_200_OK)
def get_all_customers(
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization: Only "Customer Care" role can view customers
    roles=["superadmin","Admin"]
    if current_user.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only Admins are allowed."
        )

    customers = db.query(Customer).order_by(Customer.created_at.desc()).all()

    if not customers:
        return {
            "status": "success",
            "message": "No customers found.",
            "data": []
        }

    customer_list = []
    for cust in customers:
        customer_list.append({
            "customer_code": cust.customer_code,
            "full_name": f"{cust.first_name} {cust.last_name or ''}".strip(),
            "email": cust.email,
            "phone_number": cust.phone_number,
            "account_type": cust.account_type,
            "status": cust.status,
            "city": cust.city,
            "country": cust.country,
            "created_at": cust.created_at,
        })

    return {
        "status": "success",
        "total_customers": len(customer_list),
        "data": customer_list
    }


# ------------------------------------------------------
# 🟢 GET — Customer by ID (Customer Code)
# ------------------------------------------------------

@router.get("/get-customer", status_code=status.HTTP_200_OK)
def get_customer_by_code(
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization
    if current_user.role != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only Customer care allowed."
        )
    

    customer = db.query(Customer).filter(Customer.login_id == current_user.user_table_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer found with name '{customer.first_name}'."
        )

    return {
        "status": "success",
        "message": f"Customer details for {customer.first_name}.",
        "data": {
            "customer_code": customer.customer_code,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "date_of_birth": customer.date_of_birth,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "email": customer.email,
            "phone_number": customer.phone_number,
            "alternate_phone": customer.alternate_phone,
            "address": {
                "address_line1": customer.address_line1,
                "address_line2": customer.address_line2,
                "city": customer.city,
                "state": customer.state,
                "country": customer.country,
                "postal_code": customer.postal_code,
            },
            "identity_info": {
                "national_id_number": customer.national_id_number,
                "passport_number": customer.passport_number,
                "pan_number": customer.pan_number,
                "kyc_status": customer.kyc_status,
                "kyc_verified_date": customer.kyc_verified_date,
            },
            "account_info": {
                "account_type": customer.account_type,
                "status": customer.status,
                "occupation": customer.occupation,
                "annual_income": customer.annual_income,
            },
            "profile": {
                "profile_photo": customer.profile_photo,
                "signature_image": customer.signature_image,
                "notes": customer.notes,
            },
            "created_at": customer.created_at,
            "updated_at": customer.updated_at
        }
    }



@router.put("/update-identity/{customer_code}", status_code=status.HTTP_200_OK)
async def update_customer_identity(
    national_id_number: str = Form(None),
    passport_number: str = Form(None),
    aadhaar_number: str = Form(None),
    driving_license_number: str = Form(None),
    voter_id_number: str = Form(None),
    pan_number: str = Form(None),
    national_id_file: UploadFile = File(None),
    passport_file: UploadFile = File(None),
    aadhaar_file: UploadFile = File(None),
    driving_license_file: UploadFile = File(None),
    voter_id_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "Customer":
        raise HTTPException(403, "Only Customer care allowed")

    customer = db.query(Customer).filter(Customer.login_id == current_user.user_table_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    async def save_file(file: UploadFile, code: str, doc_type: str):
        if file:
            ext = os.path.splitext(file.filename)[1]
            path = os.path.join(UPLOAD_DIR, f"{code}_{doc_type}_{timestamp}{ext}")
            with open(path, "wb") as f:
                f.write(await file.read())
            return path
        return None
    customer_code = customer.customer_code
    # Save files only if provided
    customer.national_id_path = await save_file(national_id_file, customer_code, "national_id") or customer.national_id_path
    customer.passport_path = await save_file(passport_file, customer_code, "passport") or customer.passport_path
    customer.aadhaar_path = await save_file(aadhaar_file, customer_code, "aadhaar") or customer.aadhaar_path
    customer.driving_license_path = await save_file(driving_license_file, customer_code, "driving_license") or customer.driving_license_path
    customer.voter_id_path = await save_file(voter_id_file, customer_code, "voter_id") or customer.voter_id_path

    # Update numbers only if provided
    customer.national_id_number = national_id_number or customer.national_id_number
    customer.passport_number = passport_number or customer.passport_number
    customer.aadhaar_number = aadhaar_number or customer.aadhaar_number
    customer.driving_license_number = driving_license_number or customer.driving_license_number
    customer.voter_id_number = voter_id_number or customer.voter_id_number
    customer.pan_number = pan_number or customer.pan_number

    db.commit()
    db.refresh(customer)

    return {
        "status": "success",
        "message": f"Identity documents updated for customer {customer_code}.",
        "data": {
            "national_id_number": customer.national_id_number,
            "passport_number": customer.passport_number,
            "aadhaar_number": customer.aadhaar_number,
            "driving_license_number": customer.driving_license_number,
            "voter_id_number": customer.voter_id_number,
            "pan_number": customer.pan_number,
            "national_id_path": customer.national_id_path,
            "passport_path": customer.passport_path,
            "aadhaar_path": customer.aadhaar_path,
            "driving_license_path": customer.driving_license_path,
            "voter_id_path": customer.voter_id_path
        }
    }
    
class FileType(str, Enum):
    PROFILE = "profile"
    SIGNATURE = "signature"
    NATIONAL_ID = "national_id"
    PASSPORT = "passport"
    AADHAAR = "aadhaar"
    DRIVING_LICENSE = "driving_license"
    VOTER_ID = "voter_id"

@router.get("/file", status_code=200)
def get_customer_file(
    file_type: FileType = Query(...),  # file_type from form
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization
    if current_user.role != "Customer":
        raise HTTPException(403, "Only Customer care allowed.")

    # Check customer exists
    customer = db.query(Customer).filter(Customer.login_id == current_user.user_table_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found.")

    # Map file_type to attribute
    file_map = {
        FileType.PROFILE: customer.profile_photo,
        FileType.SIGNATURE: customer.signature_image,
        FileType.NATIONAL_ID: customer.national_id_path,
        FileType.PASSPORT: customer.passport_path,
        FileType.AADHAAR: customer.aadhaar_path,
        FileType.DRIVING_LICENSE: customer.driving_license_path,
        FileType.VOTER_ID: customer.voter_id_path,
    }

    file_path = file_map.get(file_type)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"No {file_type.value} file found for customer {customer.login_id}.")

    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, media_type="application/octet-stream", filename=filename)

