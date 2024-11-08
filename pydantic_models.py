from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class Event(BaseModel):
    title: str
    created: bool
    # Add any other fields that might be in the event

class Structured(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    emoji: Optional[str] = None
    category: Optional[str] = None
    actionItems: Optional[List[str]] = []
    events: Optional[List[Event]] = []  # Changed from List[str] to List[Event]

class TranscriptSegment(BaseModel):
    text: str
    speaker: Optional[str] = None
    speaker_id: Optional[int] = None
    is_user: Optional[bool] = None
    start: Optional[float] = None
    end: Optional[float] = None

class Memory(BaseModel):
    structured: Optional[Structured] = None
    transcript_segments: Optional[List[TranscriptSegment]] = None
    geolocation: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = []
    plugins_results: Optional[List[Dict[str, Any]]] = None
    external_data: Optional[Dict[str, Any]] = None
    discarded: Optional[bool] = False
    deleted: Optional[bool] = False
    visibility: Optional[str] = "private"
    processing_memory_id: Optional[str] = None
    status: Optional[str] = "completed"