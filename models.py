from sqlalchemy import Column, String, Boolean, JSON, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MemoryDB(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(TIMESTAMP)
    started_at = Column(TIMESTAMP)
    finished_at = Column(TIMESTAMP)
    source = Column(String)
    language = Column(String)
    structured = Column(JSON)
    transcript_segments = Column(JSON)
    geolocation = Column(JSON, nullable=True)
    photos = Column(JSON)
    plugins_results = Column(JSON)
    external_data = Column(JSON, nullable=True)
    discarded = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    visibility = Column(String, default="private")
    processing_memory_id = Column(String, nullable=True)
    status = Column(String)