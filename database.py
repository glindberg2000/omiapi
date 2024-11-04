from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use the DATABASE_URL from environment variables or a default value
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://omi_user:securepassword123@localhost:5433/omi_data")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base() 