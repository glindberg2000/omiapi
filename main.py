from fastapi import FastAPI, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine, vector_engine
from models import MemoryDB, Base
from pydantic_models import Memory
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy import and_, desc
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

# Create all tables with vector engine
Base.metadata.create_all(bind=vector_engine)

app = FastAPI(
    title="Memory Management API",
    description="API for managing and retrieving memory data.",
    version="1.0.0",
    servers=[
        {"url": "https://omi.ella-ai-care.com/", "description": "Production server"}
    ]
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

client = OpenAI()

async def generate_embedding(text: str) -> list[float]:
    """Generate embedding for the given text using OpenAI's API."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

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
        
        logger.info(f"Received memory with events structure: {memory.structured.events if memory.structured else 'No structured data'}")
        
        # Generate embedding from the memory content
        text_parts = []
        
        if memory.structured:
            if memory.structured.title:
                text_parts.append(memory.structured.title)
            if memory.structured.overview:
                text_parts.append(memory.structured.overview)
        
        if memory.transcript_segments:
            transcript_texts = [seg.text for seg in memory.transcript_segments if seg.text]
            text_parts.extend(transcript_texts)
        
        text_to_embed = " ".join(text_parts)
        if not text_to_embed.strip():
            text_to_embed = "Empty memory"  # Fallback for empty content
            
        embedding = await generate_embedding(text_to_embed)
        
        # Insert into the database with embedding
        memory_db = MemoryDB(
            user_id=uid,
            embedding=embedding,
            **memory.model_dump()
        )
        db.add(memory_db)
        db.commit()
        db.refresh(memory_db)

        return {"status": "success", "memory_id": str(memory_db.id)}
    except Exception as e:
        logger.error(f"Error processing /memory-created: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

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
    limit: Optional[int] = Query(1, description="Limit the number of memories returned"),
    include_transcripts: bool = Query(False, description="Whether to include full transcripts"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(MemoryDB).filter(MemoryDB.user_id == user_id)

        # Sort memories by creation date in descending order to get the latest first
        query = query.order_by(desc(MemoryDB.created_at))

        # Limit the number of memories returned
        query = query.limit(limit)

        memories = query.all()

        # Prepare the response based on the include_transcripts flag
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

# Add a new endpoint for semantic search
@app.get("/memories/search")
async def search_memories(
    user_id: str = Query(..., description="User ID to filter memories"),
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    try:
        # Generate embedding for the search query
        query_embedding = await generate_embedding(query)
        
        # Perform vector similarity search
        results = db.query(
            MemoryDB
        ).filter(
            MemoryDB.user_id == user_id
        ).order_by(
            MemoryDB.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
        
        return [
            {
                "id": memory.id,
                "created_at": memory.created_at,
                "structured": memory.structured,
                "status": memory.status
            }
            for memory in results
        ]
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))