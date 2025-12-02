# Discord LLM AI Chatbot

Discord bot powered by Google Gemini and DeepSeek AI with conversation management, relationship tracking, and user profiling.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph External["External Systems"]
        DISCORD[("Discord API")]
        GEMINI_API[("Gemini API")]
        DEEPSEEK_API[("DeepSeek API")]
    end

    subgraph Application["Discord Bot Application"]
        subgraph EntryPoint["Entry Point"]
            BOT["bot.py<br/>Discord.py Client<br/>Auto-discovers Cogs"]
        end

        subgraph MessagePipeline["Message Processing Pipeline"]
            LLM_MSG["LLMMessageService<br/>─────────────────<br/>• Message deduplication<br/>• Processed ID tracking"]
            MSG_PROC["MessageProcessor<br/>─────────────────<br/>• Anti-spam (5 msg/min)<br/>• Rate limiting"]
            CONV_MGR["ConversationManager<br/>─────────────────<br/>• Per-user locking<br/>• Concurrent user support"]
        end

        subgraph ContextLayer["Context Assembly Layer"]
            CTX_BUILD["ContextBuilder<br/>─────────────────<br/>• Builds enhanced prompts<br/>• Aggregates user data"]
            HIST_SVC["HistoryService<br/>─────────────────<br/>• Conversation history<br/>• Message formatting"]
        end

        subgraph BusinessServices["Business Services Layer"]
            SUM_SVC["SummaryService<br/>─────────────────<br/>• User profile management<br/>• Smart update triggers<br/>• AI summary generation"]
            REL_SVC["RelationshipService<br/>─────────────────<br/>• User relationships<br/>• Interaction tracking<br/>• Server summaries"]
        end

        subgraph RepositoryLayer["Repository Layer (Data Access)"]
            SUM_DATA["SummaryDataManager<br/>─────────────────<br/>• User summary I/O<br/>• History file access"]
            REL_DATA["RelationshipDataManager<br/>─────────────────<br/>• Relationships I/O<br/>• Interactions I/O<br/>• User names mapping"]
            SUM_PARSE["SummaryParser<br/>─────────────────<br/>• Text cleaning<br/>• JSON parsing<br/>• Field merging"]
        end

        subgraph AIServices["AI Integration Layer"]
            GEMINI_SVC["GeminiService<br/>─────────────────<br/>• Prompt building<br/>• API communication<br/>• Response splitting"]
            DEEPSEEK_SVC["DeepSeekService<br/>─────────────────<br/>• Alternative AI<br/>• Backup provider"]
            TYPING["TypingSimulation<br/>─────────────────<br/>• Human-like delays<br/>• WPM calculation"]
        end

        subgraph CommandsCogs["Discord Commands (Cogs)"]
            QUEUE_CMD["QueueCommands<br/>• !queue_status<br/>• !clear_queue"]
            TYPING_CMD["TypingCommands<br/>• !test_typing<br/>• !typing_settings"]
            USER_CMD["UserCommands<br/>• !status<br/>• !relationships"]
        end

        subgraph DataStorage["JSON Data Storage"]
            PROMPTS[("prompts/<br/>─────────<br/>personality.json<br/>conversation_prompt.json<br/>summary_prompt.json<br/>summary_format.json<br/>task_instruction.json")]
            SUMMARIES[("user_summaries/<br/>─────────<br/>{user_id}_summary.json<br/>{user_id}_history.json")]
            RELATIONS[("relationships/<br/>─────────<br/>relationships.json<br/>interactions.json<br/>user_names.json")]
        end
    end

    %% External connections
    DISCORD <--> BOT
    GEMINI_SVC --> GEMINI_API
    DEEPSEEK_SVC --> DEEPSEEK_API

    %% Message pipeline flow
    BOT --> LLM_MSG
    LLM_MSG --> MSG_PROC
    MSG_PROC --> CONV_MGR
    CONV_MGR --> CTX_BUILD

    %% Context building
    CTX_BUILD --> SUM_SVC
    CTX_BUILD --> REL_SVC
    CTX_BUILD --> HIST_SVC

    %% Business to Repository
    SUM_SVC --> SUM_DATA
    SUM_SVC --> SUM_PARSE
    REL_SVC --> REL_DATA

    %% Repository to Storage
    SUM_DATA --> SUMMARIES
    REL_DATA --> RELATIONS

    %% AI flow
    CTX_BUILD --> GEMINI_SVC
    CTX_BUILD --> DEEPSEEK_SVC
    GEMINI_SVC --> PROMPTS
    DEEPSEEK_SVC --> PROMPTS
    GEMINI_SVC --> TYPING
    DEEPSEEK_SVC --> TYPING
    TYPING --> DISCORD

    %% Commands
    BOT --> QUEUE_CMD
    BOT --> TYPING_CMD
    BOT --> USER_CMD

    %% Styling
    style External fill:#1a1a2e,color:#fff
    style MessagePipeline fill:#16213e,color:#fff
    style ContextLayer fill:#0f3460,color:#fff
    style BusinessServices fill:#533483,color:#fff
    style RepositoryLayer fill:#e94560,color:#fff
    style AIServices fill:#0d7377,color:#fff
    style DataStorage fill:#14274e,color:#fff
    style CommandsCogs fill:#394867,color:#fff
```

## Message Flow Sequence

```mermaid
flowchart TD
    START((User sends message)) --> BOT[bot.py receives event]
    
    BOT --> DEDUP{LLMMessageService<br/>Already processed?}
    DEDUP -->|Yes| SKIP[Skip duplicate]
    DEDUP -->|No| SPAM{MessageProcessor<br/>Spam check}
    
    SPAM -->|Rate exceeded| WARN[Send spam warning]
    SPAM -->|OK| LOCK{ConversationManager<br/>Acquire user lock}
    
    LOCK -->|User busy| QUEUE[Queue message]
    LOCK -->|Lock acquired| CTX[ContextBuilder]
    
    CTX --> FETCH["Fetch parallel data"]
    
    subgraph DataFetch["Data Fetching"]
        FETCH --> SUM[SummaryService<br/>Get user profile]
        FETCH --> REL[RelationshipService<br/>Get relationships]
        FETCH --> HIST[HistoryService<br/>Get conversation]
    end
    
    SUM --> BUILD[Build enhanced prompt]
    REL --> BUILD
    HIST --> BUILD
    
    BUILD --> AI{Select AI Service}
    AI -->|Primary| GEMINI[GeminiService]
    AI -->|Backup| DEEPSEEK[DeepSeekService]
    
    GEMINI --> PROMPT[Load prompts from JSON]
    DEEPSEEK --> PROMPT
    
    PROMPT --> GEN[Generate AI response]
    GEN --> TYPING[Typing simulation<br/>Human-like delay]
    
    TYPING --> SEND[Send to Discord]
    SEND --> UNLOCK[Release user lock]
    UNLOCK --> UPDATE[Update user data]
    
    UPDATE --> SAVE_SUM[Save summary]
    UPDATE --> SAVE_REL[Save relationships]
    
    SAVE_SUM --> DONE((Done))
    SAVE_REL --> DONE
    
    SKIP --> DONE
    WARN --> DONE
    QUEUE --> DONE
```

## Design Patterns

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| Repository | `SummaryDataManager`, `RelationshipDataManager` | Abstract JSON file I/O operations |
| Service Layer | `SummaryService`, `RelationshipService` | Business logic and orchestration |
| Parser | `SummaryParser` | Pure text transformation without I/O |
| Command (Cog) | `QueueCommands`, `TypingCommands` | Modular Discord commands |
| Pipeline | Message processing chain | Sequential message handling |
| Singleton | `Config` | Centralized configuration |

## Project Structure

```
src/
├── bot.py                          # Entry point, Cog auto-discovery
├── config/
│   ├── settings.py                 # Config class with pathlib paths
│   └── logging_config.py           # Logging setup
├── data/
│   ├── prompts/                    # AI prompt templates (JSON)
│   ├── user_summaries/             # User profiles (gitignored)
│   └── relationships/              # Relationship data (gitignored)
├── services/
│   ├── ai/
│   │   ├── gemini_service.py       # Gemini API integration
│   │   └── deepseek_service.py     # DeepSeek API integration
│   ├── commands/
│   │   ├── queue_commands.py       # Queue management commands
│   │   └── typing_commands.py      # Typing simulation commands
│   ├── conversation/
│   │   ├── conversation_manager.py # Per-user locking
│   │   ├── message_processor.py    # Anti-spam
│   │   └── anti_spam_service.py    # Rate limiting
│   ├── messeger/
│   │   ├── llm_message_service.py  # Message deduplication
│   │   ├── context_builder.py      # Context assembly
│   │   └── message_queue.py        # Message queuing
│   ├── relationship/
│   │   ├── relationship_service.py # Relationship business logic
│   │   └── relationship_data.py    # Repository for relationships
│   └── user_summary/
│       ├── summary_service.py      # Summary business logic
│       ├── summary_data.py         # Repository for summaries
│       └── summary_parser.py       # Text parsing utilities
└── tests/                          # pytest test suite (67 tests)
```

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd discord-bot-gemini
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run
python src/bot.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_LLM_BOT_TOKEN` | Yes | Discord bot token |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key (backup) |
| `LLM_MODEL` | No | Model name (default: gemini-2.0-flash) |
| `ENABLE_TYPING_SIMULATION` | No | Enable typing delays (default: 1) |
| `TYPING_SPEED_WPM` | No | Words per minute (default: 250) |

## Bot Commands

| Command | Description |
|---------|-------------|
| `!ping` | Test bot responsiveness |
| `!status` | Check bot status and user info |
| `!relationships [user]` | View user relationships |
| `!queue_status` | Show message queue status |
| `!test_typing` | Test typing simulation |

## Testing

```bash
python -m pytest src/tests -v
# 67 passed in 0.72s
```

| Test File | Coverage |
|-----------|----------|
| `test_summary_data.py` | SummaryDataManager repository |
| `test_summary_parser.py` | SummaryParser transformations |
| `test_relationship_data.py` | RelationshipDataManager repository |
| `test_queue_commands.py` | QueueCommands Cog |
| `test_typing_commands.py` | TypingCommands Cog |
| `test_prompts.py` | Prompt file validation |

## Security

- `.env` is gitignored - never commit API keys
- Pre-commit hooks scan for secrets
- User data directories are gitignored

```bash
# Enable git hooks
powershell -ExecutionPolicy Bypass -File scripts\enable_git_hooks.ps1
```

## License

MIT License - see LICENSE file for details.
