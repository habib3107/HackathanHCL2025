import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # DATABASE_URL=os.getenv("DATABASE_URL","mysql+pymysql://root:3107habi@127.0.0.1:3306/hackathon_db") #local testing
    DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./hackathon.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "nhaibkiibtrhaa31072709")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "180"))
    SMTP_PORT_SSL = int(os.getenv("SMTP_PORT_SSL", "465"))
    SMTP_PORT_TLS = int(os.getenv("SMTP_PORT_TLS", "587"))

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "techhabib711@gmail.com")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "techhabib711@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "ndxddhsgyyevhuyn")
    
    ALLOWED_EMAIL_DOMAINS=os.getenv(
        "ALLOWED_EMAIL_DOMAINS",
        {"gmail.com", "yahoo.com", "outlook.com","iattechnologies.com","iatsolutions.co"}
)
    RESET_URL = os.getenv("RESET_URL", "http://localhost:3000/login/resetpassword")
    
settings=Settings()





# REDIS_HOST=os.getenv("REDIS_HOST", "capable-grouper-60775.upstash.io")
    # REDIS_PORT=int(os.getenv("REDIS_PORT", "6379"))
    # REDIS_DB=int(os.getenv("REDIS_DB", "0"))
    # REDIS_PASSWORD=os.getenv("REDIS_PASSWORD", "Ae1nAAIncDE0NTBjYWI5NDc2YWQ0NTE1OWJjNjY1NjM0OWExMGQyNXAxNjA3NzU")

    # SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    # SENDER_EMAIL = os.getenv("SENDER_EMAIL", "techhabib711@gmail.com")
    # SMTP_USERNAME = os.getenv("SMTP_USERNAME", "techhabib711@gmail.com")
    # SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "ndxddhsgyyevhuyn")
