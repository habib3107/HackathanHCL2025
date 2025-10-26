from app.core.database import Base
from sqlalchemy import Column,Integer,String,DateTime,Enum,Boolean,TIMESTAMP,func,DATE,Text
from datetime import datetime
from sqlalchemy.orm import relationship

class LoginUser(Base):
    __tablename__ = "login_user"

    user_table_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(20), unique=True, index=True)
    username = Column(String(150), nullable=True)
    email = Column(String(60), nullable=False)
    phone_number = Column(String(20), nullable=False)
    password = Column(String(200), nullable=False)
    hashed_password = Column(String(300), nullable=False)
    First_name = Column(String(250), nullable=True)
    Last_name = Column(String(250), nullable=True)
    Gender = Column(String(20), nullable=False)
    DOB = Column(DATE, nullable=True)
    role = Column(String(100), default='user', nullable=False)
    is_delete = Column(Boolean, default=False)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), default=datetime.now(), nullable=True)
    photo = Column(Text, nullable=True)

    employee_role=Column(String(100), nullable=True)
    department=Column(String(100), nullable=True)
    manager=Column(String(100), nullable=True)
    join_date=Column(DATE, nullable=True) 
    location=Column(String(100), nullable=True)
    address=Column(String(450), nullable=True)
    country=Column(String(50), nullable=True)


    customers = relationship("Customer",back_populates="login_user",foreign_keys="Customer.login_id")

    kyc_verified = relationship("Customer", back_populates="kyc_verified_by", foreign_keys="Customer.kyc_verified_id")
    approved_loans = relationship("Loan", back_populates="approver", foreign_keys="Loan.approved_by")
