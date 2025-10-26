from sqlalchemy.orm import Session

from app.models.login_user import LoginUser
from app.models.CustomerModel import Customer
from app.models.LoanModel import Loan

def generate_user_code(db:Session, role:str) -> str:
    if role == "superadmin":
        prefix= "SRU"
    elif role == "Admin":
        prefix= "ADM"
    elif role == "Customer":
        prefix = "CST"
    elif role == "Auditor":
        prefix = "AUD"
    else:
        prefix = "USR"
    
    last_user = db.query(LoginUser).filter(LoginUser.user_id.startswith(prefix)).order_by(LoginUser.user_id.desc()).first()
    
    if last_user and last_user.user_id[4:].isdigit():
        last_number = int(last_user.user_id[4:])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"

def generate_Customer_code(db:Session) -> str:
    prefix = "CUST"
    last_user = db.query(Customer).filter(Customer.customer_code.startswith(prefix)).order_by(Customer.customer_code.desc()).first()

    if last_user and last_user.customer_code[4:].isdigit():
        last_number = int(last_user.customer_code[4:])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"

def generate_Loan_code(db:Session) -> str:
    prefix = "LL"
    last_user = db.query(Loan).filter(Loan.loan_code.startswith(prefix)).order_by(Loan.loan_code.desc()).first()

    if last_user and last_user.loan_code[4:].isdigit():
        last_number = int(last_user.loan_code[4:])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:04d}"