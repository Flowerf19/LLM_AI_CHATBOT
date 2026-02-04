from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ServerStatistics(BaseModel):
    total_users: int = 0
    active_users: int = 0
    total_messages: int = 0
    total_relationships: int = 0
    average_messages_per_user: float = 0.0

class RelationshipEdge(BaseModel):
    user1_id: str
    user2_id: str
    strength: float
    relationship_type: str

class CommunityGroup(BaseModel):
    group_id: str
    members: List[str]
    common_interests: List[str]
    description: str

class TrendAnalysis(BaseModel):
    growing_topics: List[str] = Field(default_factory=list)
    declining_topics: List[str] = Field(default_factory=list)
    new_users: List[str] = Field(default_factory=list)

class ServerSummary(BaseModel):
    """File: data/server_summary.json"""
    server_id: str
    server_name: str
    generated_at: datetime = Field(default_factory=datetime.now)
    period: str = "daily" # or "realtime_aggregate"
    
    statistics: ServerStatistics = Field(default_factory=ServerStatistics)
    community_vibe: Optional[str] = None
    notable_events: List[str] = Field(default_factory=list)
    
    # Graph data
    relationship_graph: List[RelationshipEdge] = Field(default_factory=list)
    detected_communities: List[CommunityGroup] = Field(default_factory=list)
    
    trends: TrendAnalysis = Field(default_factory=TrendAnalysis)