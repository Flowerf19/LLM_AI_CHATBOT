# Discord LLM Chatbot - AI Coding Guidelines

## Architecture Overview
Modular Discord bot with AI-powered conversations (Gemini/DeepSeek). Uses **Repository Pattern** for data access and **Single Responsibility Principle** throughout.

### Design Patterns Applied
- **Repository Pattern**: `SummaryDataManager`, `RelationshipDataManager` handle JSON I/O
- **Service Layer**: Business logic separated from data access
- **Command Pattern**: `QueueCommands`, `TypingCommands` as separate Cog modules
- **Parser Pattern**: `SummaryParser` for text transformation (no I/O)

### Message Flow
```
Discord Gateway
    ↓
bot.py (entry point, auto-discovers Cogs)
    ↓
LLMMessageService (deduplication)
    ↓
MessageProcessor (anti-spam check)
    ↓
ConversationManager (per-user lock)
    ↓
ContextBuilder (assembles context)
    ├── SummaryService → SummaryDataManager (JSON)
    ├── RelationshipService → RelationshipDataManager (JSON)
    └── HistoryService (conversation history)
    ↓
GeminiService / DeepSeekService (AI generation)
    ↓
Typing simulation → Discord response
```

**Key Directories:**
- `src/bot.py`: Entry point, auto-discovers services via `rglob('*.py')` in `src/services/`
- `src/services/`: Discord.py Cogs with `async def setup(bot)` for dynamic loading
- `src/config/settings.py`: Centralized config using `pathlib.Path`
- `src/data/prompts/`: JSON prompt templates (personality, summary, task instructions)
- `src/data/user_summaries/`: User profile JSON files
- `src/data/relationships/`: Relationship tracking JSON files

## Service Pattern (CRITICAL)
Every service file MUST have a module-level `setup()` function:
```python
from discord.ext import commands

class MyService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):  # Required for dynamic loading
    await bot.add_cog(MyService(bot))
```

**Inter-service communication:** `self.bot.get_cog('ServiceName')` with None fallback:
```python
admin_service = self.bot.get_cog('AdminChannelsService')
is_bot_channel = admin_service.is_bot_channel(guild_id, channel_id) if admin_service else True
```

## Repository Pattern (Data Access)
All JSON I/O goes through data manager classes:
```python
# SummaryDataManager - user summaries
data_manager = SummaryDataManager()
summary = data_manager.get_user_summary(user_id)
data_manager.save_user_summary(user_id, summary)

# RelationshipDataManager - relationships & interactions
data_manager = RelationshipDataManager(data_dir)
relationships = data_manager.load_relationships()
data_manager.save_relationships(relationships)
```

**Parser classes are pure transformations (no I/O):**
```python
# SummaryParser - text parsing only
parser = SummaryParser()
cleaned = parser.clean_text(raw_text)
fields = parser.parse_to_dict(cleaned)
json_str = parser.format_to_json(fields)
```

## Path Resolution
Use `Config` paths from `settings.py` (never hardcode):
```python
from config.settings import Config
filepath = Config.PROMPTS_DIR / "personality.json"  # src/data/prompts/
history_file = Config.USER_SUMMARIES_DIR / f"{user_id}_history.json"
```

## Prompt Management
All prompts stored as JSON in `src/data/prompts/`:
- `personality.json` - Bot character/personality
- `conversation_prompt.json` - Conversation guidelines
- `summary_prompt.json` - User summary generation
- `summary_format.json` - Summary JSON schema
- `task_instruction.json` - Task instructions for AI
- `server_relationships_prompt.json` - Relationship analysis

**Loading prompts (must raise FileNotFoundError if missing):**
```python
prompt_path = Config.PROMPTS_DIR / 'summary_prompt.json'
if not prompt_path.exists():
    raise FileNotFoundError(f"Prompt not found: {prompt_path}")
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_content = f.read()
```

## Concurrency Patterns
- **Per-user locking** (not global): `ConversationManager.active_users: Set[str]` allows concurrent users
- **Message deduplication:** `_processed_message_ids = set()` prevents reprocessing
- **Anti-spam:** 5 messages/minute limit with 30s cooldown

## Context Building
`ContextBuilder.build_enhanced_context()` assembles: user summary → relationships → mentioned users → conversation history. Prompts use Vietnamese section headers (`=== NGƯỜI ĐANG NÓI CHUYỆN ===`).

## Data Storage
JSON files in `src/data/`. Naming: `{user_id}_history.json`, `{user_id}_summary.json`

## Environment Variables
Required: `DISCORD_LLM_BOT_TOKEN`, `GEMINI_API_KEY`
Optional: `DEEPSEEK_API_KEY`, `LLM_MODEL`, `ENABLE_TYPING_SIMULATION`, `TYPING_SPEED_WPM`

## Development & Testing
```powershell
python -m venv venv; venv\Scripts\activate
pip install -r requirements.txt
# Create .env, then: python src/bot.py

# Run tests
python -m pytest src/tests -v
```

### Test Files
- `test_summary_data.py` - SummaryDataManager repository tests
- `test_summary_parser.py` - SummaryParser transformation tests
- `test_relationship_data.py` - RelationshipDataManager repository tests
- `test_queue_commands.py` - QueueCommands Cog tests
- `test_typing_commands.py` - TypingCommands Cog tests
- `test_prompts.py` - Prompt file validation tests

GPU options: `requirements-gpu-cuda.txt`, `requirements-gpu-rocm.txt`, `requirements-gpu-intel.txt`

## Key Conventions
- **Logging:** `logger = logging.getLogger('discord_bot.ServiceName')` with emoji prefixes (✅❌⚠️🔒)
- **Commands:** `!` prefix, implemented as `@commands.command()` in Cogs
- **Bot mentions:** Check `self.bot.user.mentioned_in(message)`, clean with `<@{bot_id}>` removal
- **Channel filtering:** `AdminChannelsService.is_bot_channel()` for response gating
- **All I/O is async:** Use `await` for file/network operations
- **No hardcoded prompts:** All prompts loaded from JSON files

## Scripts
- `scripts/clean_pycache.py`: Remove cache
- `scripts/validate_jsons.py`: Validate data files
- `scripts/setup.py`: Environment setup
