import re
from fastapi import HTTPException, status
def validate_email(email: str):
    """Validate email format using regex."""
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format."
        )

def validate_phone_number(phone_number: str):
    """Validate phone number (10–15 digits, optional + prefix)."""
    pattern = r"^\+?[0-9]{10,15}$"
    if not re.match(pattern, phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Use only digits (10–15), optionally starting with +."
        )