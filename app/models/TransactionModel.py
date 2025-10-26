from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class TransactionTypeEnum(str, enum.Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String(255), nullable=True)

    account = relationship("Account", back_populates="transactions")
