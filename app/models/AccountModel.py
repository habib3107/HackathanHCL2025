from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class AccountTypeEnum(str, enum.Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"
    FD = "FD"

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers_table.customer_table_id"), nullable=False)
    account_type = Column(String(20), nullable=False)
    balance = Column(Float, default=0.0)
    secret_code = Column(String(10), nullable=True)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
