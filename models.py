from sqlalchemy import Column, String, Boolean, JSON, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from database import vector_engine

Base = declarative_base()

class MemoryDB(Base):
    __tablename__ = "omi_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True))
    started_at = Column(TIMESTAMP(timezone=True))
    finished_at = Column(TIMESTAMP(timezone=True))
    source = Column(String)
    language = Column(String)
    structured = Column(JSONB)
    transcript_segments = Column(JSONB)
    geolocation = Column(JSONB, nullable=True)
    photos = Column(JSONB)
    plugins_results = Column(JSONB)
    external_data = Column(JSONB, nullable=True)
    discarded = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    visibility = Column(String, default="private")
    processing_memory_id = Column(String, nullable=True)
    status = Column(String)
    embedding = Column(Vector(1536))

# When creating tables
Base.metadata.create_all(bind=vector_engine)  # Use vector_engine instead of engine