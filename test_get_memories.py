import pytest
import httpx
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MemoryDB
from datetime import datetime
import uuid

# Use a placeholder user ID for testing
TEST_USER_ID = "test-user-id-12345"

@pytest.fixture(scope="function")
def setup_db():
    # Setup: Create a new database session
    db = SessionLocal()
    try:
        # Wipe existing records for the test user
        db.query(MemoryDB).filter(MemoryDB.user_id == TEST_USER_ID).delete()
        db.commit()

        # Insert test memories
        for i in range(3):
            test_memory = MemoryDB(
                id=str(uuid.uuid4()),
                user_id=TEST_USER_ID,  # Use the placeholder user ID
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow(),
                source="test-source",
                language="en",
                structured={"title": f"Test Memory {i+1}", "overview": "Test overview", "emoji": "🧠", "category": "test", "actionItems": [], "events": []},
                transcript_segments=[{"text": "Sample text", "speaker": "SPEAKER_01", "speaker_id": 1, "is_user": True, "start": 0.0, "end": 1.0}],
                geolocation=None,
                photos=[],
                plugins_results=[],
                external_data=None,
                discarded=False,
                deleted=False,
                visibility="private",
                processing_memory_id=None,
                status="completed"
            )
            db.add(test_memory)
        db.commit()
        yield
    finally:
        # Teardown: Close the database session
        db.close()

@pytest.mark.asyncio
async def test_get_latest_memory(setup_db):
    base_url = "http://localhost:9080"  # Use your local server URL
    endpoint = "/memories/"
    params = {
        "user_id": TEST_USER_ID
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}{endpoint}", params=params)
        assert response.status_code == 200
        memories = response.json()
        assert len(memories) == 1  # Default to returning only the latest memory
        assert "transcript_segments" not in memories[0]  # Default to not including transcripts

@pytest.mark.asyncio
async def test_get_multiple_memories(setup_db):
    base_url = "http://localhost:9080"
    endpoint = "/memories/"
    params = {
        "user_id": TEST_USER_ID,
        "limit": 3
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}{endpoint}", params=params)
        assert response.status_code == 200
        memories = response.json()
        assert len(memories) == 3  # Requesting multiple memories
        assert all("transcript_segments" not in memory for memory in memories)  # Default to not including transcripts

@pytest.mark.asyncio
async def test_get_memory_with_transcripts(setup_db):
    base_url = "http://localhost:9080"
    endpoint = "/memories/"
    params = {
        "user_id": TEST_USER_ID,
        "include_transcripts": True
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}{endpoint}", params=params)
        assert response.status_code == 200
        memories = response.json()
        assert len(memories) == 1  # Default to returning only the latest memory
        assert "transcript_segments" in memories[0]  # Include transcripts when requested 