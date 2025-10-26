from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Float, ForeignKey, func, Text

from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class Customer(Base):
    __tablename__ = "customers_table"

    customer_table_id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False)

    # Basic Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    marital_status = Column(String(50), nullable=True)

    # Contact Info
    email = Column(String(120), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    alternate_phone = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)

    # Identity / KYC
    national_id_number = Column(String(100), nullable=True)
    passport_number = Column(String(100), nullable=True)
    aadhaar_number = Column(String(20), nullable=True)
    driving_license_number = Column(String(20), nullable=True)
    voter_id_number = Column(String(20), nullable=True)
    national_id_path = Column(String(255), nullable=True)
    passport_path = Column(String(255), nullable=True)
    aadhaar_path = Column(String(255), nullable=True)
    driving_license_path = Column(String(255), nullable=True)
    voter_id_path = Column(String(255), nullable=True)
    pan_number = Column(String(20), nullable=True)
    kyc_status = Column(String(20), default="Pending")
    kyc_verified_date = Column(DateTime, nullable=True)
    kyc_verified_id=Column(Integer, ForeignKey("login_user.user_table_id"), nullable=True)
    # Account Info
    account_type = Column(String(20), nullable=False)
    status = Column(String(20), default="Active")

    # Optional / Profile
    profile_photo = Column(String(255), nullable=True)
    signature_image = Column(String(255), nullable=True)
    occupation = Column(String(100), nullable=True)
    annual_income = Column(String(20), nullable=True)
    risk_category = Column(String(20), default="Low")
    notes = Column(Text, nullable=True)

    login_id = Column(Integer, ForeignKey("login_user.user_table_id"), nullable=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    login_user = relationship("LoginUser", back_populates="customers", foreign_keys=[login_id])
    kyc_verified_by = relationship("LoginUser", back_populates="kyc_verified",foreign_keys=[kyc_verified_id])
    
    accounts = relationship("Account", back_populates="customer")
    loans = relationship("Loan", back_populates="customer")