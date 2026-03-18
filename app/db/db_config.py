from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:////home/my/AI_Agent/clinic.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)