# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Update with your MySQL credentials
username = "root"
password = ""
host = "localhost"
port = "3306"
database = "plainsail_laravel"

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
