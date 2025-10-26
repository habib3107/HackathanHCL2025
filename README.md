# Hackathon Banking System API

[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.5-brightgreen)](https://fastapi.tiangolo.com/) [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-blue)](https://www.sqlalchemy.org/) [![MySQL](https://img.shields.io/badge/MySQL-8.0-yellow)](https://www.mysql.com/)

A robust, scalable backend API for a modern banking system built during a hackathon. This FastAPI-based application manages user authentication, customer onboarding, KYC verification, account operations (deposits/withdrawals), and loan processing with EMI calculations. It emphasizes security (JWT auth, password hashing), role-based access control (RBAC), and file handling for documents.

Designed for high performance and ease of use, it supports real-time operations with a MySQL database and includes CORS for frontend integration (e.g., React/Vue on port 3000).

## 🚀 Features

- **User Authentication & Management**:
  - Secure login/logout with JWT tokens (short/long-lived based on "remember me").
  - Role-based signup (Customer, Admin, Auditor, Superadmin).
  - Superadmin-only: Create/update/delete users, view all users.

- **Customer Onboarding**:
  - Create customers with profile/signature uploads.
  - Validate emails/phones, generate unique customer codes (e.g., `CUST0001`).
  - Role-restricted: Customers can only manage their own profiles.

- **KYC Verification**:
  - Upload identity documents (Aadhaar, Passport, PAN, etc.).
  - Admin/Auditor: View KYC details, approve/reject with timestamps.
  - File serving for secure document access.

- **Account Management**:
  - Create savings/current/FD accounts with initial deposits (min. thresholds).
  - Deposit/withdrawal with secret code verification.
  - Transaction history and balance inquiries.

- **Loan Processing**:
  - Apply for loans with supporting docs and auto-EMI calculation.
  - Admin review: Approve/reject with reasons/notes.
  - View personal/all loans (role-based).

- **Security & Utilities**:
  - Password hashing (bcrypt), JWT with expiration.
  - File uploads to `uploads/` directory with timestamps.
  - Unique ID generation for users/customers/loans.
  - CORS enabled for local dev (localhost:3000).

## 🛠 Tech Stack

- **Framework**: FastAPI (async, auto-docs via Swagger/OpenAPI)
- **Database**: SQLAlchemy ORM + MySQL (or SQLite for testing)
- **Auth**: JWT (PyJWT), Passlib (bcrypt)
- **Validation**: Pydantic, custom regex for emails/phones
- **File Handling**: Multipart uploads with FastAPI's `UploadFile`
- **Other**: Python 3.12, Uvicorn (ASGI server), Dotenv (env vars), Enum for types

## 📦 Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/hackathon-banking-api.git
   cd hackathon-banking-api
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt  # Create this file with: fastapi, uvicorn, sqlalchemy, pymysql, python-jose[cryptography], passlib[bcrypt], python-multipart, python-dotenv, pytz
   ```

   *Note*: Add a `requirements.txt` file to your repo for easy setup.

4. **Database Setup**:
   - Install MySQL 8.0+ and create the database:
     ```sql
     CREATE DATABASE hackathon_db;
     ```
   - Run migrations (automatic on startup via `Base.metadata.create_all`).
   - Initial superadmin user (`SRU0001`) is auto-created on first run.

## 🏃‍♂️ Running the Application

- **Development Mode** (with auto-reload):
  ```bash
  python -m app.main  # Or: uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
  ```

- **Production Mode**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

- **Access API Docs**:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

The app starts with a welcome endpoint: `GET /` → `{"MESSAGE": "Welcome to Hackathon Banking System API"}`.

### Default Superadmin Credentials
For initial access after setup, use these default credentials to log in as Superadmin (change them immediately in production for security):

- **Email**: gsjn711@gmail.com
- **Password**: 3107@Habi
- **User ID**: SRU0001
- **Role**: superadmin

## 📋 API Endpoints Overview

### Authentication
| Method | Endpoint              | Description                  | Auth Required | Role Restrictions |
|--------|-----------------------|------------------------------|---------------|-------------------|
| POST   | `/login`             | Login with email/password    | No            | All               |
| POST   | `/logout`            | Blacklist token              | Yes           | All               |
| POST   | `/signup`            | Register customer            | No            | N/A               |
| POST   | `/admin-signup`      | Register admin/auditor       | Yes           | Superadmin        |
| GET    | `/get_users`         | List all users               | Yes           | Superadmin        |
| PUT    | `/update/{user_id}`  | Update user                  | Yes           | Superadmin        |
| DELETE | `/delete/{user_id}`  | Delete user                  | Yes           | Superadmin        |

### Customers
| Method | Endpoint                          | Description                  | Auth Required | Role Restrictions     |
|--------|-----------------------------------|------------------------------|---------------|-----------------------|
| POST   | `/create`                         | Create customer profile      | Yes           | Customer              |
| GET    | `/get-all-customer`               | List all customers           | Yes           | Admin/Superadmin      |
| GET    | `/get-customer`                   | View own profile             | Yes           | Customer              |
| PUT    | `/update-identity/{customer_code}`| Upload ID docs               | Yes           | Customer              |
| GET    | `/file?file_type=...`             | Download file                | Yes           | Customer              |

### KYC
| Method | Endpoint                              | Description                  | Auth Required | Role Restrictions         |
|--------|---------------------------------------|------------------------------|---------------|---------------------------|
| GET    | `/get-customer-kyc?customer_code=...` | View KYC details             | Yes           | Admin/Auditor/Superadmin  |
| PUT    | `/update-kyc/{customer_code}`         | Approve/reject KYC           | Yes           | Admin/Superadmin          |
| GET    | `/file_kyc?customer_code=...&file_type=...` | Download KYC file       | Yes           | Admin/Auditor/Superadmin  |

### Accounts
| Method | Endpoint                          | Description                  | Auth Required | Role Restrictions |
|--------|-----------------------------------|------------------------------|---------------|-------------------|
| POST   | `/accounts/create`                | Create account               | Yes           | Admin             |
| POST   | `/accounts/deposit`               | Deposit funds                | No            | N/A               |
| POST   | `/accounts/withdraw`              | Withdraw funds               | Yes           | Account Owner     |
| GET    | `/accounts/transactions/{account_number}` | Transaction history   | Yes           | Account Owner     |
| GET    | `/accounts/balance/{account_number}` | Check balance            | Yes           | Account Owner     |

### Loans
| Method | Endpoint                  | Description                  | Auth Required | Role Restrictions |
|--------|---------------------------|------------------------------|---------------|-------------------|
| POST   | `/loans/apply`            | Apply for loan               | Yes           | Customer          |
| GET    | `/loans/my-loans`         | View personal loans          | Yes           | Customer          |
| PUT    | `/{loan_id}/review`       | Approve/reject loan          | Yes           | Admin             |
| GET    | `/loans/all-loans`        | View all loans               | Yes           | Admin             |

*Full docs at `/docs`. All endpoints include error handling (400/401/403/404/500).*

## 🧪 Example Test Cases

Below are sample curl commands to test key endpoints. Assume the API is running at `http://localhost:8000`. Replace placeholders (e.g., `<token>`) as needed. Responses are formatted JSON for clarity.

### 1. Login as Superadmin
**Request**:
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gsjn711@gmail.com&password=3107@Habi&remember_me=true"
```

**Expected Response** (200 OK):
```json
{
  "user_id": "SRU0001",
  "name": "Habib",
  "role": "superadmin",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

### 2. Signup as Customer
**Request**:
```bash
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=John Doe&email=john@example.com&phone_number=+1234567890&password=SecurePass123&first_name=John&last_name=Doe&gender=MALE&dob=1990-01-01&role=Customer"
```

**Expected Response** (201 Created):
```json
{
  "status": "success",
  "message": "User registered successfully.",
  "data": {
    "user_id": "CST0001",
    "username": "John Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "role": "Customer"
  }
}
```

### 3. Create Customer Profile (Authenticated as Customer)
**Request** (Use token from login in Authorization header):
```bash
curl -X POST "http://localhost:8000/create" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "first_name=Jane&last_name=Smith&date_of_birth=1985-05-15&gender=FEMALE&email=jane@example.com&phone_number=+1987654321&address_line1=123 Main St&city=New York&state=NY&country=USA&postal_code=10001&account_type=Savings&national_id_number=ID123"
```

**Expected Response** (201 Created):
```json
{
  "status": "success",
  "message": "Customer created successfully.",
  "data": {
    "customer_code": "CUST0001",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "status": "Active"
  }
}
```

### 4. Apply for Loan (Authenticated as Customer)
**Request**:
```bash
curl -X POST "http://localhost:8000/loans/apply" \
  -H "Authorization: Bearer <access_token>" \
  -F "loan_type=Personal" \
  -F "amount=50000" \
  -F "tenure_months=12" \
  -F "interest_rate_annual=8.0" \
  -F "loan_reason=Home Renovation" \
  -F "supporting_doc=@/path/to/document.pdf"
```

**Expected Response** (201 Created):
```json
{
  "status": "success",
  "message": "Loan application submitted successfully.",
  "data": {
    "loan_id": "LL0001",
    "loan_type": "Personal",
    "amount": 50000.0,
    "tenure_months": 12,
    "emi": 4396.42,
    "status": "Pending"
  }
}
```

### 5. Approve Loan (Authenticated as Admin)
**Request**:
```bash
curl -X PUT "http://localhost:8000/loans/LL0001/review" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=approve&additional_notes=Approved based on credit score"
```

**Expected Response** (200 OK):
```json
{
  "status": "success",
  "message": "Loan approved successfully.",
  "data": {
    "loan_id": "LL0001",
    "loan_type": "Personal",
    "amount": 50000.0,
    "status": "Approved",
    "customer_name": "Jane Smith",
    "approved_at": "2025-10-26T10:30:00Z"
  }
}
```

*Tip*: Use tools like Postman or Insomnia for easier testing with file uploads and auth headers. Check Swagger UI for interactive testing.

## 🔒 Security Notes

- **JWT Tokens**: Expire in 3 hours (default); extendable to 30 days.
- **RBAC**: Enforced via `get_current_user` dependency.
- **File Uploads**: Sanitized filenames, stored in `uploads/` (add to `.gitignore`).
- **Validation**: Email/phone regex, min deposit checks, doc requirements for KYC/loans.
- **Potential Improvements**: Add rate limiting (SlowAPI), email notifications (via SMTP), Redis for token blacklisting.

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push to branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Feedback welcome—let's make this production-ready!

## 📞 Contact

- **Author**: Habib Rahman
- **Email**: gsjn711@gmail.com


Built with ❤️ for the hackathon. Star the repo if it helps! ⭐
