from fastapi import FastAPI
from app.api.pre_start.init__db import init
from app.core.database import Base ,engine
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from app.api.main import api_router
# from app.functions.schedulars_on import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    Base.metadata.create_all(bind=engine)
    init()
    
    yield  # startup complete, app is running
    # Optionally, add shutdown logic here if needed


app=FastAPI(
    title="Hackathon Backing system",
    description="CUSTOMIZED FASTAPI Hackathon Backing system ENDPOINT",
    version="1.0.5",
    contact={
        "Name":"Habib Rahman",
        "Email":"gsjn711@gmail.com"
    },
    
    lifespan=lifespan
)


app.include_router(api_router)

origins = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def start_msg():
    return {"MESSAGE":"Welcome to Hackathon Backing system API"}

#app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) #for local development



# to run this python -m app.main