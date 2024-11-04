from fastapi import FastAPI, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import MemoryDB, Base
from pydantic_models import Memory
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy import and_

# Set up logging
logger = logging.getLogger(__name__)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/memory-created")
async def handle_memory_created(
    request: Request,
    uid: str = Query(..., description="User ID associated with the memory"),
    db: Session = Depends(get_db)
):
    try:
        # Parse JSON body into Memory model
        data = await request.json()
        memory = Memory(**data)
        
        # Log the incoming data
        logger.info(f"Memory created for user {uid}: {memory.structured.title}")
        logger.info(f"Memory details: {memory}")

        # Insert into the database
        memory_db = MemoryDB(user_id=uid, **memory.model_dump())
        db.add(memory_db)
        db.commit()
        db.refresh(memory_db)

        return {"status": "success", "memory_id": memory.id}
    except Exception as e:
        logger.error(f"Error processing /memory-created: {e}")
        raise HTTPException(status_code=400, detail="Invalid request payload")

#https://omi.ella-ai-care.com/realtime-transcript
@app.post("/realtime-transcript")
async def handle_realtime_transcript(request: Request):
    try:
        # Parse the incoming JSON payload
        data = await request.json()
        # Log the received data
        logger.info(f"Received /realtime-transcript data: {data}")
        # Process the data as needed
        return {"status": "success", "received_data": data}
    except Exception as e:
        logger.error(f"Error processing /realtime-transcript: {e}")
        raise HTTPException(status_code=400, detail="Invalid request payload")

@app.get("/memories/")
def get_memories(
    user_id: str = Query(..., description="User ID to filter memories"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering memories"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering memories"),
    include_transcripts: bool = Query(False, description="Whether to include full transcripts"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(MemoryDB).filter(MemoryDB.user_id == user_id)

        # Filter by date range if provided
        if start_date and end_date:
            query = query.filter(and_(MemoryDB.created_at >= start_date, MemoryDB.created_at <= end_date))

        # Retrieve memories
        memories = query.all()

        # Format the response
        response = []
        for memory in memories:
            memory_data = {
                "id": memory.id,
                "created_at": memory.created_at,
                "structured": memory.structured,
                "status": memory.status
            }
            if include_transcripts:
                memory_data["transcript_segments"] = memory.transcript_segments
            response.append(memory_data)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/memory-created")
# async def handle_memory_created(request: Request):
#     try:
#         # Parse the incoming JSON payload
#         data = await request.json()
#         # Log the received data
#         logger.info(f"Received /memory-created data: {data}")
#         # Process the data as needed
#         return {"status": "success", "received_data": data}
#     except Exception as e:
#         logger.error(f"Error processing /memory-created: {e}")
#         raise HTTPException(status_code=400, detail="Invalid request payload")