import pytest
from httpx import AsyncClient, ASGITransport
from main import app  # Import your FastAPI app
import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models import MemoryDB
from datetime import datetime

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
async def test_memory_created(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Generate a unique ID for the test
        unique_id = str(uuid.uuid4())
        user_id = TEST_USER_ID  # Use the placeholder user ID

        # Define the payload for the test
        payload = {
            "id": unique_id,
            "created_at": "2023-11-04T12:00:00",
            "started_at": "2023-11-04T12:00:00",
            "finished_at": "2023-11-04T12:30:00",
            "source": "test-source",
            "language": "en",
            "structured": {
                "title": "Dining Out Decision",
                "overview": "The conversation revolves around deciding on a restaurant to dine at.",
                "emoji": "🍣",
                "category": "social",
                "actionItems": [],
                "events": []
            },
            "transcript_segments": [
                {
                    "text": "Hello",
                    "speaker": "SPEAKER_01",
                    "speaker_id": 1,
                    "is_user": True,
                    "start": 0.0,
                    "end": 1.0
                }
            ],
            "geolocation": {"lat": 0.0, "lon": 0.0},
            "photos": ["photo1.jpg"],
            "plugins_results": [],
            "external_data": {"external": "data"},
            "discarded": False,
            "deleted": False,
            "visibility": "private",
            "processing_memory_id": None,
            "status": "completed"
        }

        # Send a POST request to the /memory-created endpoint with the user ID
        response = await ac.post(f"/memory-created?uid={user_id}", json=payload)

        # Assert the response status code and content
        assert response.status_code == 200
        assert response.json() == {"status": "success", "memory_id": unique_id}

@pytest.mark.asyncio
async def test_retrieve_memories(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_id = TEST_USER_ID  # Use the placeholder user ID

        # Send a GET request to the /memories/ endpoint
        response = await ac.get(f"/memories/?user_id={user_id}")

        # Assert the response status code and content
        assert response.status_code == 200
        memories = response.json()
        assert len(memories) > 0  # Ensure at least one memory is returned
        assert memories[0]["structured"]["title"] == "Test Memory 1"