from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schema import Base

DATABASE_URL = "sqlite:///./db.sqlite3"

# Create DB engine and session
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Called on startup to create tables
def init_db():
    Base.metadata.create_all(bind=engine)
