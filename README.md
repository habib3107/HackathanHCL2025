Hackathon Banking System API
  
A robust, scalable backend API for a modern banking system built during a hackathon. This FastAPI-based application manages user authentication, customer onboarding, KYC verification, account operations (deposits/withdrawals), and loan processing with EMI calculations. It emphasizes security (JWT auth, password hashing), role-based access control (RBAC), and file handling for documents.
Designed for high performance and ease of use, it supports real-time operations with a MySQL database and includes CORS for frontend integration (e.g., React/Vue on port 3000).
🚀 Features

User Authentication & Management:

Secure login/logout with JWT tokens (short/long-lived based on "remember me").
Role-based signup (Customer, Admin, Auditor, Superadmin).
Superadmin-only: Create/update/delete users, view all users.


Customer Onboarding:

Create customers with profile/signature uploads.
Validate emails/phones, generate unique customer codes (e.g., CUST0001).
Role-restricted: Customers can only manage their own profiles.


KYC Verification:

Upload identity documents (Aadhaar, Passport, PAN, etc.).
Admin/Auditor: View KYC details, approve/reject with timestamps.
File serving for secure document access.


Account Management:

Create savings/current/FD accounts with initial deposits (min. thresholds).
Deposit/withdrawal with secret code verification.
Transaction history and balance inquiries.


Loan Processing:

Apply for loans with supporting docs and auto-EMI calculation.
Admin review: Approve/reject with reasons/notes.
View personal/all loans (role-based).


Security & Utilities:

Password hashing (bcrypt), JWT with expiration.
File uploads to uploads/ directory with timestamps.
Unique ID generation for users/customers/loans.
CORS enabled for local dev (localhost:3000).



🛠 Tech Stack

Framework: FastAPI (async, auto-docs via Swagger/OpenAPI)
Database: SQLAlchemy ORM + MySQL (or SQLite for testing)
Auth: JWT (PyJWT), Passlib (bcrypt)
Validation: Pydantic, custom regex for emails/phones
File Handling: Multipart uploads with FastAPI's UploadFile
Other: Python 3.12, Uvicorn (ASGI server), Dotenv (env vars), Enum for types

📦 Installation


Clone the Repository:
bashgit clone https://github.com/yourusername/hackathon-banking-api.git
cd hackathon-banking-api


Create Virtual Environment:
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
bashpip install -r requirements.txt  # Create this file with: fastapi, uvicorn, sqlalchemy, pymysql, python-jose[cryptography], passlib[bcrypt], python-multipart, python-dotenv, pytz
Note: Add a requirements.txt file to your repo for easy setup.


Database Setup:

Install MySQL 8.0+ and create the database:
sqlCREATE DATABASE hackathon_db;

Run migrations (automatic on startup via Base.metadata.create_all).
Initial superadmin user (SRU0001) is auto-created on first run.



🏃‍♂️ Running the Application

Development Mode (with auto-reload):
bashpython -m app.main  # Or: uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Production Mode:
bashuvicorn app.main:app --host 0.0.0.0 --port 8000

Access API Docs:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc



The app starts with a welcome endpoint: GET / → {"MESSAGE": "Welcome to Hackathon Banking System API"}.
📋 API Endpoints Overview

MethodEndpointDescriptionAuth RequiredRole RestrictionsAuthPOST /loginLogin with email/passwordNoAllPOST /logoutBlacklist tokenYesAllPOST /signupRegister customerNoN/APOST /admin-signupRegister admin/auditorYesSuperadminGET /get_usersList all usersYesSuperadminPUT /update/{user_id}Update userYesSuperadminDELETE /delete/{user_id}Delete userYesSuperadminCustomersPOST /createCreate customer profileYesCustomerGET /get-all-customerList all customersYesAdmin/SuperadminGET /get-customerView own profileYesCustomerPUT /update-identity/{customer_code}Upload ID docsYesCustomerGET /file?file_type=...Download fileYesCustomerKYCGET /get-customer-kyc?customer_code=...View KYC detailsYesAdmin/Auditor/SuperadminPUT /update-kyc/{customer_code}Approve/reject KYCYesAdmin/SuperadminGET /file_kyc?customer_code=...&file_type=...Download KYC fileYesAdmin/Auditor/SuperadminAccountsPOST /accounts/createCreate accountYesAdminPOST /accounts/depositDeposit fundsNoN/APOST /accounts/withdrawWithdraw fundsYesAccount OwnerGET /accounts/transactions/{account_number}Transaction historyYesAccount OwnerGET /accounts/balance/{account_number}Check balanceYesAccount OwnerLoansPOST /loans/applyApply for loanYesCustomerGET /loans/my-loansView personal loansYesCustomerPUT /{loan_id}/reviewApprove/reject loanYesAdminGET /loans/all-loansView all loansYesAdmin
Full docs at /docs. All endpoints include error handling (400/401/403/404/500).
🔒 Security Notes

JWT Tokens: Expire in 3 hours (default); extendable to 30 days.
RBAC: Enforced via get_current_user dependency.
File Uploads: Sanitized filenames, stored in uploads/ (add to .gitignore).
Validation: Email/phone regex, min deposit checks, doc requirements for KYC/loans.
Potential Improvements: Add rate limiting (SlowAPI), email notifications (via SMTP), Redis for token blacklisting.

🤝 Contributing

Fork the repo.
Create a feature branch (git checkout -b feature/amazing-feature).
Commit changes (git commit -m 'Add amazing feature').
Push to branch (git push origin feature/amazing-feature).
Open a Pull Request.

Feedback welcome—let's make this production-ready!
📞 Contact

Author: Habib Rahman
Email: gsjn711@gmail.com
