
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    question: str = Field(..., description="User's question")


class ChatResponse(BaseModel):
    final_answer: str
    trace: Optional[Dict[str, Any]] = None

