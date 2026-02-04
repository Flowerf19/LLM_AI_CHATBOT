from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Activity(BaseModel):
    """Một hoạt động đơn lẻ (tin nhắn, join, leave)"""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    username: str
    action: str  # "message", "join", "leave", "reaction"
    content: Optional[str] = None
    channel_id: str
    mentioned_users: List[str] = Field(default_factory=list)
    
    # Metadata cho context overlap
    is_context_only: bool = Field(default=False, description="Nếu true, tin này chỉ dùng làm context (gối đầu), không thuộc batch hiện tại")

class BatchTracking(BaseModel):
    """Theo dõi trạng thái xử lý Batch"""
    current_batch_size: int = 0
    last_summary_at: Optional[datetime] = None
    total_batches_processed: int = 0
    last_critical_at: Optional[datetime] = None
    
    # New V2.1: Time Flush tracking
    first_msg_in_batch_at: Optional[datetime] = None # Để check timeout 30p

class RecentLog(BaseModel):
    """File: data/recent_log.json"""
    server_id: str
    last_updated: datetime = Field(default_factory=datetime.now)
    max_messages: int = 100
    messages: List[Activity] = Field(default_factory=list)
    batch_tracking: BatchTracking = Field(default_factory=BatchTracking)