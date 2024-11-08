from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Regular database engine (for omi_data)
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vector database engine (for omi_memories)
vector_engine = create_engine(os.getenv("PGVECTOR_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)