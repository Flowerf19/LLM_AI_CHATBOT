from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CriticalEvent(BaseModel):
    """Sự kiện quan trọng AI phát hiện được"""
    user_id: str
    username: str
    event_type: str  # "relationship_change", "life_event", "community_event"
    summary: str
    timestamp: datetime
    confidence: float
    affected_users: List[str] = Field(default_factory=list)

class BatchSummary(BaseModel):
    """Output của AI sau khi tóm tắt batch"""
    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    messages_count: int
    user_ids: List[str]
    
    # AI Analysis
    ai_summary: str
    has_critical_events: bool
    critical_events: List[CriticalEvent] = Field(default_factory=list)
    
    # Metadata
    processing_time: float
    llm_model: str