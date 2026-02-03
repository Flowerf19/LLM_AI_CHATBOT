# V2.0 Activity Diagram - RecentLog + Batch Processing

**Based on:** Real-time batch processing every 10 messages (No scheduled jobs!)

## 🔄 Main Message Flow (Real-time Batch Processing)

```mermaid
flowchart TD
    Start([User sends message]) --> Capture[MessageProcessor<br/>captures message]
    Capture --> Append[Append to RecentLog<br/>messages array]
    Append --> Truncate{RecentLog > 100<br/>messages?}
    
    Truncate -->|YES| Remove[Remove oldest<br/>messages]
    Truncate -->|NO| CheckBatch{Current batch<br/>= 10 messages?}
    Remove --> CheckBatch
    
    CheckBatch -->|NO| UpdateCounter[Increment<br/>batch counter]
    UpdateCounter --> End1([End])
    
    CheckBatch -->|YES| TriggerLLM[🤖 TRIGGER:<br/>Batch Summary Job]
    TriggerLLM --> SetBusy[Set BotStatus:<br/>busy=true]
    SetBusy --> CallLLM[AI: Summarize<br/>last 10 messages<br/>+ Detect CRITICAL]
    
    CallLLM --> SaveBatch[Save BatchSummary<br/>with results]
    SaveBatch --> AnyCritical{Critical events<br/>detected?}
    
    AnyCritical -->|NO| ResetBatch[Reset batch counter<br/>to 0]
    ResetBatch --> SetFree1[Set BotStatus:<br/>busy=false]
    SetFree1 --> End2([End])
    
    AnyCritical -->|YES| UpdateUsers[Update affected<br/>UserSummaries]
    UpdateUsers --> UpdateServer[Update<br/>ServerSummary]
    UpdateServer --> ResetBatch
    
    classDef normal fill:#51cf66,stroke:#2f9e44,color:#fff
    classDef llm fill:#da77f2,stroke:#9c36b5,color:#fff
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef decision fill:#ffd43b,stroke:#fab005,color:#000
    
    class Append,Remove,UpdateCounter,SaveBatch,ResetBatch normal
    class CallLLM,UpdateUsers,UpdateServer llm
    class TriggerLLM,AnyCritical critical
    class Truncate,CheckBatch decision
```

## 📦 Batch Summary Process (Detail)

```mermaid
flowchart TD
    Trigger([10 messages reached]) --> GetMessages[Get last 10 messages<br/>from RecentLog]
    GetMessages --> BuildPrompt[Build LLM prompt:<br/>- 10 messages content<br/>- User contexts<br/>- Critical detection guidelines]
    
    BuildPrompt --> CallOllama[Ollama API:<br/>qwen3:4b-instruct]
    CallOllama --> ParseResponse[Parse LLM response]
    
    ParseResponse --> CreateSummary[Create BatchSummary:<br/>- ai_summary<br/>- has_critical_events<br/>- critical_events list]
    
    CreateSummary --> CheckCritical{has_critical_events<br/>= true?}
    
    CheckCritical -->|NO| Log1[Log: Batch processed<br/>No critical events]
    CheckCritical -->|YES| Log2[Log: 🚨 Critical events<br/>found in batch]
    
    Log2 --> ForEachCritical{For each<br/>critical event}
    ForEachCritical -->|Next| GetUser[Get affected<br/>user_id]
    GetUser --> LoadSummary[Load UserSummary]
    LoadSummary --> AddEvent[Add CriticalEventHistory]
    AddEvent --> UpdateFacts[Update facts/<br/>relationships]
    UpdateFacts --> SaveUser[Save UserSummary]
    SaveUser --> CheckMore{More critical?}
    
    CheckMore -->|YES| ForEachCritical
    CheckMore -->|NO| AggregateServer[Update ServerSummary<br/>with changes]
    
    AggregateServer --> Done([Complete])
    Log1 --> Done
    
    classDef llm fill:#da77f2,stroke:#9c36b5,color:#fff
    classDef save fill:#51cf66,stroke:#2f9e44,color:#fff
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
    
    class CallOllama,ParseResponse llm
    class SaveUser,AggregateServer save
    class Log2,ForEachCritical,AddEvent critical
```

## 💬 Per-User Optimization (Conversation Mode)

```mermaid
flowchart TD
    Chat([Bot chatting with<br/>User A]) --> LoadCheck{Need user<br/>context?}
    
    LoadCheck -->|YES| LoadUserA[Load ONLY<br/>User A's summary]
    LoadCheck -->|NO| SkipLoad[Skip loading]
    
    LoadUserA --> Use[Use for context<br/>in AI response]
    Use --> UpdateRecent[Update RecentLog<br/>with new message]
    
    UpdateRecent --> Skip29[Skip loading<br/>29 other users]
    Skip29 --> WaitBatch([Wait for batch trigger<br/>at 10 messages])
    SkipLoad --> UpdateRecent
    
    Note1[🎯 Optimization:<br/>- 0 LLM calls during chat<br/>- Just file I/O<br/>- Lazy loading]
    
    classDef optimize fill:#69db7c,stroke:#2f9e44,color:#fff
    classDef skip fill:#868e96,stroke:#495057,color:#fff
    
    class LoadUserA,Use optimize
    class Skip29,SkipLoad skip
```

## 📊 RecentLog Lifecycle

```mermaid
flowchart TD
    Start([Bot Startup]) --> LoadRecent[Load recent_log.json<br/>from disk]
    LoadRecent --> CheckValid{Valid format?}
    
    CheckValid -->|NO| CreateNew[Create new<br/>RecentLog]
    CheckValid -->|YES| Continue[Continue from<br/>saved state]
    
    CreateNew --> Running[Bot Running]
    Continue --> Running
    
    Running --> Messages{Messages<br/>arriving?}
    Messages -->|YES| Process[Process message<br/>+ Batch check]
    Messages -->|Continue| Running
    
    Process --> Running
    
    Shutdown([Shutdown Signal]) --> SaveState[Save RecentLog<br/>to disk]
    SaveState --> Stop([Bot Stopped])
    
    classDef lifecycle fill:#4dabf7,stroke:#1864ab,color:#fff
    
    class LoadRecent,SaveState,Running lifecycle
```

## 🤖 LLM Critical Detection Logic

```
During batch processing (every 10 messages):

Input to LLM:
- Last 10 messages with full content
- User contexts for participants  
- Critical event guidelines

LLM Task:
1. Summarize batch (what happened overall)
2. Detect if any CRITICAL events occurred
   Examples:
   - Relationship changes (marriage, breakup, new love)
   - Life events (job change, moving, graduation)
   - Community impact (major conflicts, user leaving)
   - Personality shifts (dramatic mood/behavior changes)

Output JSON:
{
  "batch_summary": "Users discussed bot development...",
  "has_critical_events": true/false,
  "critical_events": [
    {
      "user_id": "123",
      "event_type": "life_event",
      "summary": "User started new job",
      "confidence": 0.9,
      "affected_users": []
    }
  ]
}

Benefits:
✅ 10-message context (enough for detection)
✅ Real-time (max 10 msg delay = ~5 minutes typically)
✅ No keyword maintenance
✅ AI understands nuance
✅ Event-driven (no wasted processing)
```

## 📊 Data Flow Simplified

```
Messages → RecentLog (sliding window 100)
           ↓ (every 10 messages)
         LLM Batch Summary
           ↓ (if critical detected)
      UserSummary + ServerSummary
```

**Storage:**
- Temporary: RecentLog (100 messages, rolling)
- Permanent: UserSummary.critical_events[]
- Permanent: ServerSummary

---

## 📝 Key Benefits

✅ **Simple:** 1 file, 1 trigger, 0 scheduled jobs  
