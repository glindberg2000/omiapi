from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TranscriptSegment(BaseModel):
    text: Optional[str] = None
    speaker: Optional[str] = None
    speaker_id: Optional[int] = None
    is_user: Optional[bool] = None
    start: Optional[float] = None
    end: Optional[float] = None

class StructuredData(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    emoji: Optional[str] = None
    category: Optional[str] = None
    actionItems: Optional[List[str]] = Field(default_factory=list)
    events: Optional[List[str]] = Field(default_factory=list)

class Memory(BaseModel):
    id: Optional[str] = None
    created_at: Optional[str] = None
    structured: Optional[StructuredData] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    transcript_segments: Optional[List[TranscriptSegment]] = Field(default_factory=list)
    plugins_results: Optional[List[Dict]] = Field(default_factory=list)
    geolocation: Optional[Dict] = None
    photos: Optional[List[str]] = Field(default_factory=list)
    discarded: Optional[bool] = None
    deleted: Optional[bool] = None
    source: Optional[str] = None
    language: Optional[str] = None
    external_data: Optional[Dict] = None
    status: Optional[str] = None