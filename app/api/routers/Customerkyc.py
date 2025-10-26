
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
from app.enumsfolder.CustomerEnum import GenderEnum, MaritalStatusEnum,AccountTypeEnum,KYCStatusEnum
router = APIRouter()

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

@router.get("/get-customer-kyc", status_code=status.HTTP_200_OK)
def get_customer_by_code_kyc(
    customer_code: str = Query(..., description="Unique customer code to fetch details"),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization
    role_allowed = ["Admin", "superadmin", "Auditor"]

    if current_user.role not in role_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    # Fetch customer by code
    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer found with code '{customer_code}'."
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
                "aadhaar_number": customer.aadhaar_number,
                "driving_license_number": customer.driving_license_number,
                "voter_id_number": customer.voter_id_number,
                "pan_number": customer.pan_number,
                "kyc_status": customer.kyc_status,
                "kyc_verified_date": customer.kyc_verified_date,
                "kyc_verified_by": customer.kyc_verified_by.First_name + " " + (customer.kyc_verified_by.Last_name or "") if customer.kyc_verified_by else None,
                "national_id_path": customer.national_id_path,
                "passport_path": customer.passport_path,
                "aadhaar_path": customer.aadhaar_path,
                "driving_license_path": customer.driving_license_path,
                "voter_id_path": customer.voter_id_path
            },
            "account_info": {
                "account_type": customer.account_type,
                "status": customer.status,
                "occupation": customer.occupation,
                "annual_income": customer.annual_income,
                "risk_category": customer.risk_category
            },
            "profile": {
                "profile_photo": customer.profile_photo,
                "signature_image": customer.signature_image,
                "notes": customer.notes,
            },
            "audit": {
                "created_at": customer.created_at,
                "updated_at": customer.updated_at
            }
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
@router.get("/file_kyc", status_code=200)
def get_customer_file(
    customer_code: str = Query(..., description="Unique customer code"),
    file_type: FileType = Query(...),  # file_type from form
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization
    role_allowed = ["Admin", "superadmin", "Auditor"]
    if current_user.role not in role_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )

    # Check customer exists
    customer = db.query(Customer).filter(Customer.customer_code== customer_code).first()
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

@router.put("/update-kyc/{customer_code}", status_code=status.HTTP_200_OK)
def update_customer_kyc(
    customer_code: str,
    kyc_status: KYCStatusEnum = Form(None),
    
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Authorization check
    role_allowed = ["Admin", "superadmin"]
    if current_user.role not in role_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update KYC."
        )

    # Fetch customer by code
    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer found with code '{customer_code}'."
        )

    # Update fields if provided
    if customer.aadhaar_number and customer.aadhaar_path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update KYC status. Aadhaar number provided but Aadhaar document not uploaded."
        )
    if customer.passport_number and customer.passport_path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update KYC status. Passport number provided but Passport document not uploaded."
        )
    if customer.driving_license_number and customer.driving_license_path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update KYC status. Driving License number provided but Driving License document not uploaded."
        )
    if customer.voter_id_number and customer.voter_id_path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update KYC status. Voter ID number provided but Voter ID document not uploaded."
        )
    if customer.pan_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update KYC status. PAN number provided but PAN document not uploaded."
        )
    if kyc_status is not None:
        customer.kyc_status = kyc_status.value
        if kyc_status.value == "Verified":
            customer.kyc_verified_date = datetime.utcnow()
            customer.kyc_verified_id = current_user.user_table_id

    db.commit()
    db.refresh(customer)

    return {
        "status": "success",
        "message": f"KYC updated for customer {customer.customer_code}.",
        "data": {
            "customer_code": customer.customer_code,
            "kyc_status": customer.kyc_status,
            "kyc_verified_date": customer.kyc_verified_date
        }
    }
    
