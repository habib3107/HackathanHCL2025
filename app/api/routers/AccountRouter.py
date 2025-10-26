from fastapi import APIRouter, Depends, HTTPException, Form, status,Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.CustomerModel import Customer
from app.models.AccountModel import Account, AccountTypeEnum
from app.models.TransactionModel import Transaction, TransactionTypeEnum
from app.models.login_user import LoginUser
from app.function.validation import validate_email, validate_phone_number
from app.core.security import get_current_user
import random

router = APIRouter(prefix="/accounts")

def generate_account_number():
    # Example: 12-digit random number
    return str(random.randint(100000000000, 999999999999))

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_account(
    customer_code: str = Form(...),
    account_type: AccountTypeEnum = Form(...),
    initial_deposit: float = Form(...),
    secret_code: str = Form(...),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # 1️⃣ Fetch customer
    if not customer_code:
        raise HTTPException(status_code=400, detail="Customer code is required")
    if current_user.role not in ["Admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create accounts")
    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"No customer found with code {customer_code}")
    
    if customer.status != "Active":
        raise HTTPException(status_code=400, detail="Customer account is not active")
    if customer.kyc_status != "Verified":
        raise HTTPException(status_code=400, detail="Customer KYC is not verified")
    # 2️⃣ Validate minimum deposit
    min_deposit = 1000 if account_type == AccountTypeEnum.SAVINGS else 5000
    if initial_deposit < min_deposit:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum initial deposit for {account_type.value} is {min_deposit}"
        )

    # 3️⃣ Generate account number
    account_number = generate_account_number()

    # 4️⃣ Create account
    new_account = Account(
        account_number=account_number,
        customer_id=customer.customer_table_id,
        secret_code=secret_code,
        account_type=account_type,
        balance=initial_deposit
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # 5️⃣ Log initial deposit as transaction
    transaction = Transaction(
        account_id=new_account.account_id,
        transaction_type="Deposit",
        amount=initial_deposit,
        description="Initial deposit"
    )
    
    db.add(transaction)
    db.commit()

    return {
        "status": "success",
        "message": f"{account_type.value} account created for {customer.first_name}",
        "data": {
            "account_number": new_account.account_number,
            "account_type": new_account.account_type,
            "balance": new_account.balance
        }
    }



@router.post("/deposit", status_code=status.HTTP_200_OK)
def deposit_amount(
    account_number: str = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_db)
):
    # Fetch account
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero")

    # Update balance
    account.balance += amount
    db.add(account)

    # Log transaction
    transaction = Transaction(
        account_id=account.account_id,
        transaction_type="Deposit",
        amount=amount,
        description="Deposit"
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)

    return {
        "status": "success",
        "message": f"Deposited {amount} to account {account_number}",
        "data": {
            "account_number": account.account_number,
            "balance": account.balance
        }
    }
    
@router.post("/withdraw", status_code=status.HTTP_200_OK)
def withdraw_amount(
    account_number: str = Form(...),
    amount: float = Form(...),
    secret_code: str = Form(...),
    db: Session = Depends(get_db),
    current_user: LoginUser = Depends(get_current_user)
):
    # Fetch account
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
    if account.secret_code != secret_code:
        raise HTTPException(status_code=403, detail="Invalid secret code")
    if account.customer.login_id != current_user.user_table_id:
        raise HTTPException(status_code=403, detail="Not authorized to withdraw from this account")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be greater than zero")

    if amount > account.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Update balance
    account.balance -= amount
    db.add(account)

    # Log transaction
    transaction = Transaction(
        account_id=account.account_id,
        transaction_type="Withdrawal",
        amount=amount,
        description="Withdrawal"
    )
    db.add(transaction)
    db.commit()
    db.refresh(account)

    return {
        "status": "success",
        "message": f"Withdrawn {amount} from account {account_number}",
        "data": {
            "account_number": account.account_number,
            "balance": account.balance
        }
    }



@router.get("/transactions/{account_number}", status_code=status.HTTP_200_OK)
def get_transaction_history(
    account_number: str,
    current_user: LoginUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, description="Number of recent transactions to fetch")
):
    # Fetch account
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
    if account.customer.login_id != current_user.user_table_id:
        raise HTTPException(status_code=403, detail="Not authorized to withdraw from this account")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account.account_id)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "success",
        "message": f"Last {len(transactions)} transactions for account {account_number}",
        "current_balance": account.balance,
        "data": [
            {
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "description": t.description,
                "timestamp": t.timestamp
            }
            for t in transactions
        ]
    }


@router.get("/balance/{account_number}", status_code=status.HTTP_200_OK)
def get_account_balance(
    account_number: str,
    current_user: LoginUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch account
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
    if account.customer.login_id != current_user.user_table_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this account balance")

    return {
        "status": "success",
        "message": f"Current balance for account {account_number}",
        "data": {
            "account_number": account.account_number,
            "balance": account.balance
        }
    }