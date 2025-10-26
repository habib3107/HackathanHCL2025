from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class LoanStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class Loan(Base):
    __tablename__ = "loans"

    loan_table_id = Column(Integer, primary_key=True, index=True)
    loan_code = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers_table.customer_table_id"), nullable=False)
    loan_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)  # Principal amount (P)
    tenure_months = Column(Integer, nullable=False)  # Tenure in months (n)
    interest_rate_annual = Column(Float, nullable=False)  # Annual interest rate in percentage
    emi = Column(Float, nullable=True)  # Calculated EMI
    status = Column(String(50), default="Pending", nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("login_user.user_table_id"), nullable=True)
    loan_reason = Column(String(255), nullable=True)    
    rejection_reason = Column(String(255), nullable=True)
    supporting_document_path = Column(String(255), nullable=True)
    notes = Column(String(500), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="loans")
    approver = relationship("LoginUser", back_populates="approved_loans", foreign_keys=[approved_by])
