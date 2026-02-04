from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# --- Sub Models ---
class PersonalityProfile(BaseModel):
    traits: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    communication_style: Optional[str] = None
    tone: Optional[str] = None

class UserFacts(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    projects: List[str] = Field(default_factory=list)
    hobbies: List[str] = Field(default_factory=list)

class Relationship(BaseModel):
    other_user_id: str
    other_username: str
    relationship_type: str  # "friend", "colleague", "neutral"
    strength: float = 0.5   # 0.0 - 1.0
    interaction_count: int = 0
    first_interaction: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    notes: Optional[str] = None

class ActivitySummary(BaseModel):
    total_messages: int = 0
    active_days: int = 0
    average_messages_per_day: float = 0.0
    most_active_time: Optional[str] = None
    most_active_channels: List[str] = Field(default_factory=list)

class CriticalEventHistory(BaseModel):
    """Lưu trữ vĩnh viễn sự kiện quan trọng"""
    event_id: str
    timestamp: datetime
    event_type: str
    summary: str
    details: Optional[str] = None
    confidence: float
    
    # Impact
    affected_relationships: List[str] = Field(default_factory=list)
    personality_impact: Optional[str] = None
    
    # Source
    batch_id: str
    detected_at: datetime
    
    # V2.1: Lifecycle management
    status: str = "active"  # "active", "resolved", "archived"

# --- Main Model ---
class UserSummary(BaseModel):
    """File: data/user_profiles/{ID}/summary.json"""
    user_id: str
    username: str
    
    personality: PersonalityProfile = Field(default_factory=PersonalityProfile)
    facts: UserFacts = Field(default_factory=UserFacts)
    relationships: List[Relationship] = Field(default_factory=list)
    activity: ActivitySummary = Field(default_factory=ActivitySummary)
    
    # Chỉ lưu events thực sự quan trọng (filtered by AI)
    critical_events: List[CriticalEventHistory] = Field(default_factory=list)
    
    last_updated: datetime = Field(default_factory=datetime.now)
    total_events_tracked: int = 0