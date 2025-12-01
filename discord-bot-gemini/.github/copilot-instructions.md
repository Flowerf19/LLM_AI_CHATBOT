# Discord LLM Chatbot - AI Coding Guidelines

## Architecture Overview
This is a modular Discord bot built with `discord.py`, featuring AI-powered conversations using Gemini and DeepSeek APIs. The bot manages user relationships, conversation history, and summaries through a service-oriented architecture.

**Key Components:**
- `src/bot.py`: Main entry point that dynamically loads services as extensions
- `src/services/`: Modular services (AI, conversation, relationship, user commands)
- `src/data/prompts/`: Text files containing AI prompts (e.g., `personality.txt`, `conversation_prompt.txt`)
- `src/data/relationships/`: JSON storage for relationship data
- `src/models/`: Data models for users, channels, conversations

**Data Flow:**
Messages → `LLMMessageService` → `ContextBuilder` → `GeminiService` → Response with typing simulation

## Service Pattern
All services follow the extension pattern with `async def setup(bot)` for dynamic loading. Services are cogs that interact via `bot.get_cog()`.

**Example Service Structure:**
```python
from discord.ext import commands

class ExampleService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize dependencies
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Handle messages
    
    async def setup(bot):
        await bot.add_cog(ExampleService(bot))
```

## Configuration & Environment
Use `src/config/settings.py` for centralized config loaded from environment variables. Never hardcode API keys.

**Key Settings:**
- `GEMINI_API_KEY`, `LLM_MODEL`: AI service config
- `ENABLE_TYPING_SIMULATION`: Controls realistic typing delays
- `DISCORD_LLM_BOT_TOKEN`: Bot authentication

## AI Integration
AI responses are generated via `GeminiService` or `DeepSeekService`, enhanced with context from `ContextBuilder` including user summaries and relationship data.

**Prompt Loading Pattern:**
```python
def _load_prompt(self, filename: str) -> str:
    prompts_dir = os.path.join(src_dir, 'data', 'prompts')
    filepath = os.path.join(prompts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()
```

## Data Persistence
Use JSON files in `src/data/` for persistence. Relationship data, user summaries, and conversation history are stored as JSON.

**Path Resolution:**
Always resolve paths relative to `src/` directory to ensure correct loading across environments.

## Commands & Interactions
Commands use `!` prefix, implemented as `@commands.command` in cog classes. Bot responds to mentions or in designated channels.

**Anti-Spam & Locking:**
- `ConversationManager` prevents concurrent responses per user
- Messages queued during locks
- Cooldowns enforced via timestamps

## Development Workflow
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env`
3. Run bot: `python src/bot.py`
4. Sync slash commands: Set `SYNC_COMMANDS=1` in env

## Key Files for Reference
- `src/services/messeger/llm_message_service.py`: Main message handling logic
- `src/services/relationship/relationship_service.py`: Relationship tracking and AI summaries
- `src/services/conversation/conversation_manager.py`: Conversation locking and queuing
- `src/config/settings.py`: Configuration management</content>
<parameter name="filePath">.github/copilot-instructions.md