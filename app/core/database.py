from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker,declarative_base
from app.core.config import settings

# engine=create_engine(settings.DATABASE_URL)
engine=create_engine(settings.DATABASE_URL,connect_args={"check_same_thread": False})
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()    
        
        