# V2.0 Relationship & User Summary Refactor Design

**Branch:** `v2.0-relationship-refactor`  
**Date:** February 3, 2026  
**Status:** 🔵 PLANNING

## 🎯 Server Profile: Small Community (~30 users)

**Optimization Strategy:**
- ✅ **Real-time batch processing:** Every 10 messages → LLM summary + critical detection
- ✅ **Sliding window:** Keep only last 100 messages (no daily archive)
- ✅ **Event-driven updates:** Critical events trigger immediate UserSummary updates
- ✅ **Dead server optimized:** No scheduled jobs, no wasted polling
- ✅ **Minimal storage:** Only critical info saved permanently in UserSummary

**Trigger Philosophy:**
```
⚡ REAL-TIME BATCH (Every 10 messages) → Single trigger
   1. Buffer reaches 10 messages
   2. LLM summarizes batch → Detects critical events
   3. If critical → Update UserSummary + ServerSummary
   4. If normal → Discard summary (RecentLog keeps rolling)
   5. RecentLog maintains last 100 messages only (sliding window)

🎯 KEY BENEFITS:
   - No scheduled jobs (dead server friendly)
   - No daily archives (save storage)
   - Real-time critical detection (3-5 sec delay max)
   - Only important info persists (UserSummary)
   - Simple: 1 trigger, no midnight cascade
```

**Per-User Optimization (Quan trọng!):**
```
💬 CONVERSATION MODE (Real-time)
   - Bot đang chat với User A
   - Chỉ load summary của User A (lazy loading)
   - KHÔNG load 29 users khác (lãng phí)
   - RecentLog vẫn ghi tất cả messages (shared resource)
   
📝 UPDATE SCOPE
   Normal messages:
   - Update: Chỉ RecentLog (append to sliding window)
   - Load: Chỉ UserSummary của user đang chat (for context)
   - Skip: 29 users khác không được touch
   
   Every 10 messages (batch trigger):
   - LLM summarizes batch → Detects critical
   - If critical found in User A's messages:
     * Update ONLY User A's summary (not all 30 users)
     * Update ServerSummary (aggregate impact)
   - If normal: Discard, wait for next batch
   
🎯 KEY INSIGHT: 
   1 batch = 10 messages from mixed users
   Only users with critical events get updated
   Others wait for their critical moment
```

---

## 📋 Problem Statement

### Current Issues:
1. **Relationship tracking** - Fake data, không tự động phát hiện relationships
2. **User summary** - Bug #2: AI không extract được info từ history
3. **Missing data** - Không có cơ chế để không bỏ sót thông tin
4. **No structure** - Thiếu model rõ ràng cho daily logs và summaries

### Goals:
✅ Ghi nhật ký hàng ngày tự động  
✅ Track ai mention ai  
✅ Tóm tắt từng user định kỳ  
✅ Không bỏ sót thông tin quan trọng  
✅ Có thể đọc toàn bộ user files để aggregate summary

---

## 🏗️ New Architecture

### 1. RecentLog System (Sliding Window)

```
Single file, no daily rotation:
data/recent_log.json

⏰ LIFECYCLE:
- Persistent file, never archived
- Maintains last 100 messages only (sliding window)
- Auto-truncate: When > 100, remove oldest
- On bot shutdown: Save current state
- On bot startup: Load and continue

💾 BATCH TRIGGERS:
- Every 10 messages → LLM summarize + critical detection
- If critical → Update UserSummary + ServerSummary
- If normal → Discard summary (messages still in RecentLog)
- NO scheduled jobs needed

{
  "server_id": "1067690340359880724",
  "last_updated": "2026-02-03T15:30:00",
  "max_messages": 100,
  "current_count": 87,
  "messages": [
    {
      "timestamp": "2026-02-03T10:30:00",
      "user_id": "726302130318868500",
      "username": "Flowerf",
      "action": "message",
      "content": "Hello @BeBay",
      "mentioned_users": ["1392176240156344440"],
      "channel_id": "1395103735725821982"
    },
    // ... last 99 messages
  ],
  "batch_tracking": {
    "current_batch_size": 7,  // Next trigger at 10
    "last_summary_at": "2026-02-03T15:20:00",
    "total_batches_processed": 145
  }
}
```

### 2. User Profile System (Simplified)
```
data/user_profiles/USER_ID/
├── profile.json          # Basic info
├── relationships.json    # Who they interact with
└── summary.json         # Aggregated summary (includes critical events history)

Note: NO daily_notes/ folder - không cần daily archives!
      Critical info được LLM extract và lưu trực tiếp vào summary.json
```

**Example structures:** (See `important_keywords.json` for reference if needed for prompts)

---

## 📁 New File Structure

```
discord-bot-gemini/
└── src/
    └── data/
        ├── recent_log.json              # NEW: Sliding window (last 100 msg)
        ├── user_profiles/
        │   ├── 726302130318868500/
        │   │   ├── profile.json
        │   │   ├── relationships.json
        │   │   └── summary.json
        │   └── 1392176240156344440/
        │       └── ...
        └── server_summary.json

Note: NO daily_logs/ or daily_notes/ folders!
```
---

## 🏛️ Class Model Design

### Core Models & Schemas ✅

**Files to create:**
- [ ] `src/models/v2/recent_log.py` - RecentLog, Activity, BatchTracking
- [ ] `src/models/v2/batch_summary.py` - BatchSummary, CriticalEvent
- [ ] `src/models/v2/user_profile.py` - UserProfile
- [ ] `src/models/v2/user_summary.py` - UserSummary, PersonalityProfile, UserFacts, Relationship, ActivitySummary, CriticalEventHistory
- [ ] `src/models/v2/server_summary.py` - ServerSummary, ServerStatistics, CommunityOverview, RelationshipGraph
- [ ] `src/services/v2/data_managers/` - JSON I/O for each model

**Validation:**
- [ ] All models use Pydantic for validation
- [ ] JSON schema generation
- [ ] Unit tests for each model

### Phase 2: RecentLog System
- RecentLog service with sliding window (100 messages)
- Batch processing every 10 messages
- Integration with message processor

### Phase 3: LLM Batch Summarization
- Batch summary generation (Ollama)
- Critical event detection
- User/Server summary updates when critical

### Phase 4: Integration & Commands
- Event-driven updates (no scheduler needed!)
- Commands: !mysummary, !server, !recent
- Migration from old system
  - Remove `services/user_summary/` (old)
- Testing & error handling

---

## 🧱 Pydantic Models

#### 1. RecentLog
```python
class Activity:
    """Single activity in the log"""
    timestamp: datetime
    user_id: str
    username: str
    action: str                  # "message", "join", "leave", "reaction"
    content: Optional[str]
    channel_id: str
    mentioned_users: List[str]

class BatchTracking:
    """Track batch processing state"""
    current_batch_size: int      # 0-9, triggers at 10
    last_summary_at: datetime
    total_batches_processed: int
    last_critical_at: Optional[datetime]

class RecentLog:
    """Sliding window of recent messages"""
    server_id: str
    last_updated: datetime
    max_messages: int = 100      # Keep only last 100
    current_count: int
    messages: List[Activity]     # Auto-truncate when > max_messages
    batch_tracking: BatchTracking

#### 2. BatchSummary
```python
class CriticalEvent:
    """Critical event detected in batch"""
    user_id: str
    username: str
    event_type: str              # "relationship_change", "life_event", "community_event"
    summary: str                 # Brief description
    timestamp: datetime
    confidence: float            # 0.0-1.0
    affected_users: List[str]    # Related users

class BatchSummary:
    """LLM summary of message batch"""
    batch_id: str
    timestamp: datetime
    messages_count: int
    user_ids: List[str]          # Users in this batch
    
    # LLM output
    ai_summary: str              # Brief summary of batch
    has_critical_events: bool
    critical_events: List[CriticalEvent]  # Empty if no critical
    
    # Metadata
    processing_time: float       # Seconds
    llm_model: str              # "qwen3:4b-instruct"

#### 3. UserProfile
```python
class UserProfile:
    """Base profile information"""
    user_id: str
    username: str
    display_name: str
    real_name: Optional[str]
    first_seen: datetime
    last_active: datetime
    total_messages: int
    avatar_url: Optional[str]
```

#### 4. UserSummary
```python
class UserSummary:
    """Comprehensive user summary - MAIN MODEL"""
    user_id: str
    username: str
    
    # Personality & Interests
    personality: PersonalityProfile
    
    # Key Facts
    facts: UserFacts
    
    # Relationships
    relationships: List[Relationship]
    
    # Activity Summary
    activity: ActivitySummary
    
    # NEW: Critical Events History (Replaces daily_highlights)
    critical_events: List[CriticalEventHistory]  # Only important events stored
    
    # Metadata
    last_updated: datetime
    total_events_tracked: int
    
class CriticalEventHistory:
    """Critical events permanently stored in UserSummary"""
    timestamp: datetime
    event_type: str              # "relationship_change", "life_event", "community_event"
    summary: str                 # Brief description
    details: str                 # Full context
    confidence: float            # 0.0-1.0
    
    # Impact tracking
    affected_relationships: List[str]  # User IDs affected
    personality_impact: Optional[str]  # How this changed user's personality
    
    # Source
    batch_id: str                # Which batch detected this
    detected_at: datetime
    
class UserSummary:
    """Example JSON structure - Simplified"""
    user_id: "726302130318868500",
    username: "Flowerf",
    
    personality: {...},
    facts: {...},
    relationships: [...],
    
    critical_events: [
        {
            "timestamp": "2026-02-03T15:30:00",
            "event_type": "life_event",
            "summary": "Started working on Discord bot with Ollama",
            "details": "User announced starting new project - Discord bot using Ollama for AI. Very excited about it.",
            "confidence": 0.9,
            "affected_relationships": ["BeBay"],  # Collaborating with BeBay
            "personality_impact": "Added interest: bot development, Ollama",
            "batch_id": "batch_145",
            "detected_at": "2026-02-03T15:30:00"
        },
        {
            "timestamp": "2026-02-01T10:20:00",
            "event_type": "relationship_change",
            "summary": "Became close friends with Alice",
            "details": "User and Alice started chatting frequently, lots of positive interactions",
            "confidence": 0.85,
            "affected_relationships": ["Alice"],
            "personality_impact": null,
            "batch_id": "batch_98",
            "detected_at": "2026-02-01T10:25:00"
        }
    ],
    
    event_timeline: [
        {
            "timestamp": "2026-02-03T10:30:00",
            "event_type": "fact_learned",
            "category": "hobbies",
            "description": "Learned user likes Python programming",
            "source_date": "2026-02-03",
            "confidence": 0.95,
            "old_value": null,
            "new_value": "Python programming"
        },
        {
            "timestamp": "2026-02-03T14:20:00",
            "event_type": "relationship_change",
            "category": "relationships",
            "description": "Started collaborating with BeBay on bot project",
            "source_date": "2026-02-03",
            "confidence": 0.85,
            "old_value": null,
            "new_value": "collaborator"
        },
        {
            "timestamp": "2026-01-28T09:15:00",
            "event_type": "fact_learned",
            "category": "basic_info",
            "description": "Learned user's name is Flowerf",
            "source_date": "2026-01-28",
            "confidence": 1.0,
            "old_value": null,
            "new_value": "Flowerf"
        }
    ]
    
class PersonalityProfile:
    """AI-extracted personality"""
    traits: List[str]            # ["technical", "helpful"]
    interests: List[str]         # ["AI", "Python"]
    communication_style: str
    tone: str                    # "friendly", "formal"
    
class UserFacts:
    """Key facts about user"""
    name: Optional[str]
    age: Optional[str]
    location: Optional[str]
    occupation: Optional[str]
    projects: List[str]
    hobbies: List[str]
    
class Relationship:
    """Relationship with another user"""
    other_user_id: str
    other_username: str
    relationship_type: str       # "friend", "colleague", "collaborator"
    strength: float              # 0.0 - 1.0
    interaction_count: int
    first_interaction: datetime
    last_interaction: datetime
    notes: str                   # AI-generated relationship notes
    
class ActivitySummary:
    """Overall activity summary"""
    total_messages: int
    active_days: int
    average_messages_per_day: float
    most_active_time: str        # "morning", "afternoon", "night"
    most_active_channels: List[str]
```

#### 5. BotStatus (NEW)
```python
class BotStatus:
    """Track bot's current status for UX"""
    is_busy: bool
    current_task: Optional[str]  # "writing_daily_notes", "updating_user_summary", "generating_server_summary"
    task_progress: Optional[str] # "Processing 3/10 users"
    started_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    
class BusyResponse:
    """Auto-response when bot is busy"""
    messages: List[str] = [
        "Bé Bảy đang bận viết nhật kí, chờ tí nhé! 📝",
        "Đang tóm tắt hoạt động của mọi người, chờ xíu! ✍️",
        "Đang cập nhật thông tin server, back soon! 🔄"
    ]
```

#### 6. LLM Critical Detection (NEW - Simpler approach)
```python
# No separate model needed!
# LLM detects critical events directly in UserDailyNote generation
# Fields added to UserDailyNote:
#   - has_critical_events: bool
#   - critical_summary: Optional[str]
#   - requires_immediate_update: bool

class CriticalEventGuidelines:
    """Guidelines for LLM to detect critical events"""
    
    EXAMPLES = """
    Critical events that require immediate updates:
    
    🚨 CRITICAL (cascade now):
    - Relationship changes: Kết hôn, chia tay, có người yêu
    - Major life events: Đổi việc, nghỉ việc, chuyển nhà
    - Community impact: Major conflicts, user leaving
    - Personality shifts: Dramatic mood/behavior changes
    
    ✅ NORMAL (wait until next cycle):
    - Daily conversations
    - Minor topics
    - Regular interactions
    - Small updates
    
    LLM should use full day context to judge significance.
    Ask: "Does this change how I understand this user or the community?"
    """
    
    @staticmethod
    def get_detection_prompt() -> str:
        return f"""
        Based on this user's activities today, determine if any CRITICAL events occurred.
        
        {CriticalEventGuidelines.EXAMPLES}
        
        Return:
        - has_critical_events: true/false
        - critical_summary: Brief description if critical
        - requires_immediate_update: true if cascade needed
        """
```

#### 7. ServerSummary

```python
class ServerSummary:
    """TỔNG HỢP TẤT CẢ USER SUMMARIES"""
    server_id: str
    server_name: str
    generated_at: datetime
    period: str                  # "daily", "weekly", "monthly"
    
    # Statistics
    statistics: ServerStatistics
    
    # Community Overview
    community: CommunityOverview
    
    # Relationships Graph
    relationships_graph: RelationshipGraph
    
    # Active Users
    top_users: List[TopUserSummary]
    
    # Trends
    trends: TrendAnalysis
    
class ServerStatistics:
    """Server-wide statistics"""
    total_users: int
    active_users: int
    total_messages: int
    total_relationships: int
    average_messages_per_user: float
    
class CommunityOverview:
    """AI-generated community overview"""
    summary: str                 # AI tổng hợp từ all user summaries
    main_topics: List[str]
    community_vibe: str          # "technical", "social", "gaming"
    notable_events: List[str]
    
class RelationshipGraph:
    """Network of relationships"""
    nodes: List[UserNode]        # All users
    edges: List[RelationshipEdge] # All relationships
    communities: List[Community]  # Detected communities
    
class UserNode:
    user_id: str
    username: str
    centrality_score: float      # How central in network
    
class RelationshipEdge:
    user1_id: str
    user2_id: str
    strength: float
    relationship_type: str
    
class Community:
    """Detected community/group"""
    community_id: str
    members: List[str]
    common_interests: List[str]
    description: str
    
class TopUserSummary:
    """Condensed summary for top users"""
    user_id: str
    username: str
    message_count: int
    key_traits: List[str]
    main_interests: List[str]
    relationship_count: int
    
class TrendAnalysis:
    """Trend analysis"""
    growing_topics: List[str]
    declining_topics: List[str]
    new_users: List[str]
    most_connected_users: List[str]

---

## 📊 AI Prompts Strategy

- **Batch Summary:** Extract critical events from 10 messages with minimal context
- **User Summary:** Merge critical events into existing profile, update relationships
- **Server Summary:** Aggregate all user changes, update relationship graph

---
