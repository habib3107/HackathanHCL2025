from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.login_user import LoginUser
from datetime import datetime


def start_user(db:Session):
    try:
        new_id="SRU0001"
        first_name="Habib"
        last_name="Rahman"
        email="gsjn711@gmail.com"
        password="3107@Habi"
        phone_number=9944028646
        hashed_password=hash_password(password)
        existing_user=db.query(LoginUser).filter(LoginUser.email==email).first()

        if existing_user:
            print("already exist")
            return
        dob =datetime.strptime("31 07 2003", "%d %m %Y").date()
        initial_user=LoginUser(
            user_id=new_id,
            username=first_name+" "+last_name,
            email=email,
            password=password,
            hashed_password=hashed_password,
            phone_number=phone_number,
            role="superadmin",
            Gender="MALE",
            First_name=first_name,
            Last_name=last_name,
            DOB=dob
        )

        db.add(initial_user)
        db.commit()
        db.refresh(initial_user)
        print("Intial user create")
    except Exception as e:
        db.rollback()
        print(f"error not create {e}")

    finally:
        db.close()

def init():
    db=SessionLocal()
    try:
        start_user(db)
    finally:
        db.close()

