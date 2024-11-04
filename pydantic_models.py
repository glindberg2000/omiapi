from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TranscriptSegment(BaseModel):
    text: str
    speaker: str
    speaker_id: int
    is_user: bool
    start: float
    end: float

class StructuredData(BaseModel):
    title: str
    overview: str
    emoji: str
    category: str
    actionItems: List[Any]
    events: List[Any]

class Memory(BaseModel):
    id: str
    created_at: datetime
    structured: StructuredData
    started_at: datetime
    finished_at: datetime
    transcript_segments: List[TranscriptSegment]
    plugins_results: List[Any]
    geolocation: Optional[Dict[str, Any]] = None
    photos: List[str]
    discarded: bool
    deleted: bool
    source: str
    language: str
    external_data: Optional[Dict[str, Any]] = None
    status: str