# Discord LLM Chatbot - AI Coding Guidelines

## Project Context
V2.1 event-driven Discord bot optimized for small communities (~30 users). Uses real-time batch processing with Gemini/Ollama LLMs for context-aware conversations. NO scheduled jobs - fully reactive architecture.

## Architecture: V2.1 Batch Processing System

### Core Philosophy
**Real-time event-driven architecture** - triggers on activity, not schedules. Optimized for "dead server" scenarios (no wasted polling/cron jobs).

### Message Flow (V2.1)
```
Discord Message
    ↓
MessageProcessor.process_message()
    ├─→ Lazy Sync: Apply pending updates for returning user
    ├─→ RecentLog: Append to sliding window (max 100)
    ├─→ Hybrid Trigger: Check if 10 msgs OR 30 min timeout
    │   └─→ YES: BatchProcessor.process_batch() [background task]
    │       ├─→ Get batch + 5 context messages (Context Overlap)
    │       ├─→ Send to LLM for analysis
    │       ├─→ Extract critical events
    │       └─→ Update UserSummary + create PendingUpdates for affected users
    └─→ Reply to user (immediate, parallel to batch processing)
```

**Key Components:**
- **RecentLog** ([recent_log.py](../discord-bot/src/models/v2/recent_log.py)): Single JSON file, sliding window of last 100 messages. No daily rotation.
- **BatchProcessor** ([batch_processor.py](../discord-bot/src/services/conversation/batch_processor.py)): Every 10 messages → LLM summarization. Uses Context Overlap (5 previous messages for continuity).
- **PendingUpdateService** ([pending_update_service.py](../discord-bot/src/services/conversation/pending_update_service.py)): Lazy Sync Queue - stores relationship updates for offline users.
- **MessageProcessor** ([message_processor.py](../discord-bot/src/services/conversation/message_processor.py)): Entry point orchestrating the V2.1 flow.

### Data Models (Pydantic V2)
All models in `src/models/v2/`:
- `RecentLog`: Sliding window buffer with `BatchTracking` (batch size, timers)
- `BatchSummary`: LLM output with critical events detection
- `UserSummary`: Per-user profiles with `CriticalEventHistory`
- `SyncQueue`: Pending updates for lazy synchronization

### Thread Safety
`JsonDataManager` ([data_manager.py](../discord-bot/src/data/data_manager.py)) provides AsyncIO locks per file path:
```python
from src.data.data_manager import data_manager

# All file I/O goes through data_manager for automatic locking
await data_manager.save_model(file_path, pydantic_model)
model = await data_manager.load_model(file_path, ModelClass, default_factory)
```

## Discord.py Service Pattern (CRITICAL)
Every service MUST export `async def setup(bot)` for dynamic loading:
```python
from discord.ext import commands

class MyService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):  # Required - bot.py auto-discovers via rglob
    await bot.add_cog(MyService(bot))
```

**Inter-service communication:**
```python
admin_service = self.bot.get_cog('AdminChannelsService')
if admin_service:
    admin_service.is_bot_channel(guild_id, channel_id)
```

## Path Resolution
Use `Config` from [settings.py](../discord-bot/src/config/settings.py) (never hardcode):
```python
from src.config.settings import Config

prompt_path = Config.PROMPTS_DIR / "batch_summary_prompt.json"

# V2.1: User data now centralized in user_profiles
user_profile_dir = Path("data/user_profiles") / user_id
user_summary = user_profile_dir / "summary.json"
user_history = user_profile_dir / "history.json"
```

**Important:** All imports use `src.` prefix. Bot root is `discord-bot/`.

## Prompt Management
JSON prompts in `src/data/prompts/`:
- `batch_summary_prompt.json` - V2.1 batch analysis with context overlap format
- `personality.json` - Bot character (supports Vietnamese responses)
- `conversation_prompt.json` - Conversation guidelines

Load with validation:
```python
if not prompt_path.exists():
    raise FileNotFoundError(f"Prompt not found: {prompt_path}")
```

## Testing (pytest + asyncio)
[pytest.ini](../discord-bot/pytest.ini) configured for async tests:
```bash
# Run V2.1 unit tests
pytest tests/test_v2_1_unit.py -v

# All tests auto-cleanup with fixtures
# Tests use test_data/ directory (auto-cleaned)
```

Test structure:
- `@pytest.fixture(autouse=True)` for data cleanup
- Override service file paths to `test_data/` in fixtures
- Mark async tests with `@pytest.mark.asyncio`

## Development Workflow
```bash
# Setup
conda activate /path/to/.conda
pip install -r requirements.txt

# Required .env variables
DISCORD_LLM_BOT_TOKEN=...
GEMINI_API_KEY=...
OLLAMA_API_URL=http://localhost:11434  # Optional fallback

# Run bot
python src/bot.py

# Expected startup logs
✅ Loaded service: services.conversation.message_processor
✅ Synced X slash commands
🚀 V2.1 Features: Lazy Sync ✅ | Context Overlap ✅ | Hybrid Trigger ✅
```

## V2.1 Critical Patterns

### 1. Context Overlap (Batch Processing)
Retrieve 5 previous messages before current batch for LLM context:
```python
active_batch, context_msgs = await recent_log_service.get_batch_for_processing()
# context_msgs have is_context_only=True flag
```

### 2. Hybrid Trigger (10 msgs OR 30 min)
```python
# In RecentLogService.add_activity()
batch = log.batch_tracking
if batch.current_batch_size >= 10:  # Batch Full
    return True
elif batch.first_msg_in_batch_at and (now - batch.first_msg_in_batch_at) > 30min:  # Time Flush
    return True
```

### 3. Lazy Sync Queue
When User A's event affects offline User B:
```python
await pending_update_service.add_pending_update(
    target_user_id="user_B",
    update_type="relationship_sync",
    data={"relationship": "became_friends"}
)

# When User B returns and sends message
if await pending_update_service.has_pending_updates(user_id):
    updates = await pending_update_service.get_pending_updates(user_id)
    # Apply updates to UserSummary
    await pending_update_service.clear_pending_updates(user_id)
```

### 4. Background Task Pattern
Don't block user replies:
```python
if should_trigger_batch:
    asyncio.create_task(self._run_batch_processing(server_id))  # Fire and forget
await self._handle_bot_response(message)  # Reply immediately
```

## Key Conventions
- **Logging:** Use `from src.utils.helpers import get_logger` with emoji prefixes (✅❌⚠️⚡🔒)
- **Async everywhere:** All file/network I/O requires `await`
- **No hardcoded paths:** Always use `Config.*_DIR` constants
- **Pydantic validation:** Parse all JSON through Pydantic models (v2 syntax: `model_validate_json()`, `model_dump_json()`)
- **Documentation:** Vietnamese comments accepted in code (multilingual team)

## Architecture Decisions (Read docs/ for details)
- **Why no daily archives?** Small server - sliding window sufficient. Critical info extracted by LLM and stored in UserSummary.
- **Why event-driven?** Dead server friendly - no wasted CPU on scheduled tasks when inactive.
- **Why Lazy Sync?** Per-user optimization - only load/update affected users, not all 30 users per batch.
- **Why Context Overlap?** Ensures LLM understands conversation continuity across batch boundaries.

See [V2_DESIGN.md](../discord-bot/docs/V2_DESIGN.md), [V2.1_IMPLEMENTATION.md](../discord-bot/docs/V2.1_IMPLEMENTATION.md) for full architecture rationale.
