from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import math
import os
from app.function.generating_id import  generate_Loan_code
from app.core.database import get_db
from app.models.LoanModel import Loan
from app.models.CustomerModel import Customer 
from app.models.login_user import LoginUser  # Assuming models are imported
from app.core.security import get_current_user  # Assuming auth dependency
import enum

UPLOAD_DIR = "uploads/customers/"  # Assume utils for validations, dir

router = APIRouter(prefix="/loans", tags=["Loans"])

# EMI Calculation Function
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI using the formula:
    EMI = (P * r * (1 + r)^n) / ((1 + r)^n - 1)
    where r = monthly interest rate (annual_rate / 12 / 100), n = tenure_months
    """
    if annual_rate <= 0 or tenure_months <= 0:
        raise ValueError("Invalid rate or tenure")
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return principal / tenure_months
    power_term = math.pow(1 + monthly_rate, tenure_months)
    emi = (principal * monthly_rate * power_term) / (power_term - 1)
    return round(emi, 2)

@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def apply_for_loan(
    loan_type: str = Form(...),
    amount: float = Form(...),
    tenure_months: int = Form(...),
    interest_rate_annual: float = Form(8.0),  # Default 8%
    loan_reason : str = Form(None),
    supporting_doc: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "Customer":  # Assuming 'Customer' for customers
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only Customers allowed"
        )
    
    
    
    if amount <= 0 or tenure_months <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount and tenure must be positive."
        )

    # 🔹 Fetch customer from current user
    customer = db.query(Customer).filter(Customer.login_id == current_user.user_table_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 🔹 Check for existing pending loans (optional)
    existing_loan = db.query(Loan).filter(
        Loan.customer_id == customer.customer_table_id,
        Loan.status == "Pending"
    ).first()
    if existing_loan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending loan application."
        )
        
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    doc_path = None

    if supporting_doc:
        file_ext = os.path.splitext(supporting_doc.filename)[1]  # get extension
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        safe_filename = supporting_doc.filename.replace(" ", "_")  # optional: remove spaces
        doc_path = os.path.join(
            UPLOAD_DIR,
            f"{customer.customer_code}_loan_doc_{timestamp}{file_ext}"
        )
        with open(doc_path, "wb") as f:
            f.write(await supporting_doc.read())

    # 🔹 Calculate EMI
    emi = calculate_emi(amount, interest_rate_annual, tenure_months)

    # 🔹 Create new loan application
    new_loan = Loan(
        loan_code=generate_Loan_code(db),
        customer_id=customer.customer_table_id,
        loan_type=loan_type,
        amount=amount,
        tenure_months=tenure_months,
        interest_rate_annual=interest_rate_annual,
        emi=emi,
        loan_reason=loan_reason,
        supporting_document_path=doc_path,
        status="Pending",
        applied_at=func.now()
    )
    

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)

    return {
        "status": "success",
        "message": "Loan application submitted successfully.",
        "data": {
            "loan_id": new_loan.loan_code,
            "loan_type": new_loan.loan_type,
            "amount": new_loan.amount,
            "tenure_months": new_loan.tenure_months,
            "emi": new_loan.emi,
            "status": new_loan.status,
        }
    }
    
    
@router.get("/my-loans", status_code=status.HTTP_200_OK)
def get_my_loans(
    current_user: LoginUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only Customers allowed"
        )
    loans = (
        db.query(Loan)
        .join(Customer, Loan.customer_id == Customer.customer_table_id)
        .filter(Customer.login_id == current_user.user_table_id)
        .all()
    )

    # Optional: serialize the loans to dicts
    results = []
    for loan in loans:
        results.append({
            "loan_id": loan.loan_code,
            "loan_type": loan.loan_type,
            "amount": loan.amount,
            "tenure_months": loan.tenure_months,
            "interest_rate_annual": loan.interest_rate_annual,
            "emi": loan.emi,
            "status": loan.status,
            "applied_at": loan.applied_at,
            "approved_at": loan.approved_at,
            "rejection_reason": loan.rejection_reason,
        })

    return {"status": "success", "data": results}


class LoanAction(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"

@router.put("/{loan_id}/review", status_code=status.HTTP_200_OK)
async def review_loan(
    loan_code: str,
    action: LoanAction = Form(...),  # 'approve' or 'reject'
    additional_notes: str = Form(None),  # For approve
    rejection_reason: str = Form(None),  # For reject
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only admin allowed"
        )
    
    if action == "reject" and (not rejection_reason or len(rejection_reason.strip()) < 10):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason must be provided and at least 10 characters long"
        )
    
    
    # 🔹 Fetch the loan and check if pending
    loan = db.query(Loan).filter(
        Loan.loan_code == loan_code,
        Loan.status == "Pending"
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending loan not found"
        )
    
    # 🔹 Update based on action
    if action.value == "approve":
        loan.status = "Approved"
        loan.approved_at = datetime.utcnow()
        loan.approved_by = current_user.user_table_id
        if additional_notes:
            loan.notes = additional_notes  # Append or set notes if field exists
        message = "Loan approved successfully."
    elif action.value == "reject":
        if loan.notes is not None:
            loan.notes = None
        loan.status = "Rejected"
        loan.rejection_reason = rejection_reason
        message = "Loan rejected successfully."
    
    db.commit()
    db.refresh(loan)
    
    # 🔹 Optionally, fetch customer for response
    customer = db.query(Customer).filter(Customer.customer_table_id == loan.customer_id).first()
    
    response_data = {
        "loan_id": loan.loan_code,
        "loan_type": loan.loan_type,
        "amount": loan.amount,
        "status": loan.status,
        "customer_name": f"{customer.first_name} {customer.last_name or ''}".strip() if customer else None,
    }
    
    if action == "approve":
        response_data["approved_at"] = loan.approved_at.isoformat() if loan.approved_at else None
    else:
        response_data["rejection_reason"] = loan.rejection_reason
    
    return {
        "status": "success",
        "message": message,
        "data": response_data
    }
    
@router.get("/all-loans", status_code=status.HTTP_200_OK)
def get_all_loans(
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource. Only admin allowed"
        )

    loans = db.query(Loan).all()
    return {"status": "success",
            "data":{
                "total_loans": len(loans),
                "loans": [
                    {
                        "loan_id": loan.loan_code,
                        "loan_type": loan.loan_type,
                        "amount": loan.amount,
                        "tenure_months": loan.tenure_months,
                        "interest_rate_annual": loan.interest_rate_annual,
                        "emi": loan.emi,
                        "status": loan.status,
                        "applied_at": loan.applied_at,
                        "approved_at": loan.approved_at,
                        "rejection_reason": loan.rejection_reason,
                        
                        "customer_id": loan.customer.customer_code if loan.customer else None,
                        "customer_name": f"{loan.customer.first_name} {loan.customer.last_name or ''}".strip() if loan.customer else None,
                    }
                    for loan in loans
                ]
            }}