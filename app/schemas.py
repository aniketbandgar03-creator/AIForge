from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique conversation thread identifier")
    message: str = Field(..., description="User query or task command")
    dataset_id: Optional[str] = Field(None, description="Optional active dataset ID")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    intermediate_steps: List[str] = []


class HistoryItem(BaseModel):
    role: str
    content: str
    created_at: Any


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    columns: List[str]
    total_rows: int