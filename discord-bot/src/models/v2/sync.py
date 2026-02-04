from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class PendingUpdate(BaseModel):
    """Một yêu cầu update đang chờ (pending)"""
    target_user_id: str
    source_event_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    update_type: str  # "relationship_sync", "mention_sync"
    
    # Data cần merge vào target user
    data: Dict[str, Any] 
    # Ví dụ: { "with_user_id": "A", "new_status": "friend", "context": "..." }

class SyncQueue(BaseModel):
    """File: data/system/pending_updates.json"""
    server_id: str
    # Key: target_user_id, Value: List các update đang chờ
    queue: Dict[str, List[PendingUpdate]] = Field(default_factory=dict)
    last_processed: datetime = Field(default_factory=datetime.now)