from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class InterviewSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class InterviewSessionCreate(BaseModel):
    pass  # No additional fields needed for creation

class TranscriptEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    speaker: str = "interviewer"  # or "user"

class TranscriptCreate(BaseModel):
    session_id: str
    text: str
    speaker: str = "interviewer"

class AIResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    question: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIResponseRequest(BaseModel):
    session_id: str
    question: str

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Interview Session Management
@api_router.post("/interview/session", response_model=InterviewSession)
async def create_interview_session(input: InterviewSessionCreate):
    session_obj = InterviewSession()
    await db.interview_sessions.insert_one(session_obj.dict())
    return session_obj

@api_router.get("/interview/session/{session_id}", response_model=InterviewSession)
async def get_interview_session(session_id: str):
    session = await db.interview_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return InterviewSession(**session)

@api_router.get("/interview/sessions", response_model=List[InterviewSession])
async def get_all_sessions():
    sessions = await db.interview_sessions.find().to_list(100)
    return [InterviewSession(**session) for session in sessions]

# Transcript Management
@api_router.post("/interview/transcript", response_model=TranscriptEntry)
async def add_transcript(input: TranscriptCreate):
    # Verify session exists
    session = await db.interview_sessions.find_one({"id": input.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    transcript_obj = TranscriptEntry(**input.dict())
    await db.transcripts.insert_one(transcript_obj.dict())
    return transcript_obj

@api_router.get("/interview/transcript/{session_id}", response_model=List[TranscriptEntry])
async def get_session_transcripts(session_id: str):
    transcripts = await db.transcripts.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
    return [TranscriptEntry(**transcript) for transcript in transcripts]

# AI Response Generation
@api_router.post("/interview/ai-response", response_model=AIResponse)
async def generate_ai_response(input: AIResponseRequest):
    try:
        # Verify session exists
        session = await db.interview_sessions.find_one({"id": input.session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session context (recent transcripts)
        recent_transcripts = await db.transcripts.find(
            {"session_id": input.session_id}
        ).sort("timestamp", -1).limit(5).to_list(5)
        
        # Prepare context for AI
        context = "Recent interview conversation:\n"
        for transcript in reversed(recent_transcripts):
            context += f"{transcript['speaker']}: {transcript['text']}\n"
        
        # Create system message for interview assistance
        system_message = """You are an expert interview copilot assistant. Your role is to help the interviewee answer questions professionally and effectively.

When given an interview question, provide:
1. A clear, concise, and professional answer
2. Key points to emphasize
3. Examples or experiences to mention if relevant

Keep responses natural, authentic, and appropriate for a professional interview setting. 
Format your response to be easy to read quickly during an interview.

Structure your response as:
**Main Answer:** [Direct response to the question]
**Key Points:** [2-3 bullet points of important aspects to mention]
**Example/Experience:** [If relevant, suggest a brief example to share]"""

        # Initialize Gemini chat
        chat = LlmChat(
            api_key=os.environ.get('GEMINI_API_KEY'),
            session_id=input.session_id,
            system_message=system_message
        ).with_model("gemini", "gemini-2.5-pro-preview-05-06").with_max_tokens(1024)
        
        # Create user message with context and question
        full_prompt = f"{context}\n\nCurrent Question: {input.question}\n\nPlease provide a professional interview response:"
        user_message = UserMessage(text=full_prompt)
        
        # Get AI response
        ai_response_text = await chat.send_message(user_message)
        
        # Save the AI response
        response_obj = AIResponse(
            session_id=input.session_id,
            question=input.question,
            response=ai_response_text
        )
        await db.ai_responses.insert_one(response_obj.dict())
        
        return response_obj
        
    except Exception as e:
        logging.error(f"Error generating AI response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI response: {str(e)}")

@api_router.get("/interview/ai-responses/{session_id}", response_model=List[AIResponse])
async def get_session_ai_responses(session_id: str):
    responses = await db.ai_responses.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
    return [AIResponse(**response) for response in responses]

# Original status endpoints
@api_router.get("/")
async def root():
    return {"message": "Interview Copilot API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()