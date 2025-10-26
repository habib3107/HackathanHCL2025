from fastapi import APIRouter
from app.api.authentication import Login_out
from app.api.routers import Signup
from app.api.routers import Customer
from app.api.routers import Customerkyc
from app.api.routers import AccountRouter
from app.api.routers import LoanRouter

api_router=APIRouter()
api_router.include_router(Login_out.router,tags=["Login"])
api_router.include_router(Signup.router,tags=["Signup"])
api_router.include_router(Customer.router,tags=["Customer"])
api_router.include_router(Customerkyc.router,tags=["Customer KYC"])
api_router.include_router(AccountRouter.router,tags=["Accounts"])
api_router.include_router(LoanRouter.router,tags=["Loans"])
