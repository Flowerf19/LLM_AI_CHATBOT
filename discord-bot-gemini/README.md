# Discord LLM AI Chatbot

A sophisticated Discord bot powered by Google's Gemini and DeepSeek AI models, featuring intelligent conversation management, relationship tracking, user summaries, and anti-spam protection.

## ✨ Features

- **Multi-Model AI Support**: Integrates Gemini 2.0 Flash and DeepSeek AI for diverse response capabilities
- **Contextual Responses**: Maintains conversation history and user summaries for personalized interactions
- **Intelligent Relationships**: Tracks and analyzes user relationships with natural language recognition
- **User Profiling**: AI-generated summaries of user interactions and profiles stored as JSON
- **Conversation Management**: Anti-spam protection, message queuing, and sequential response handling
- **Typing Simulation**: Realistic typing delays to mimic human-like responses
- **Admin Controls**: Channel-based bot configuration and user commands

## 🏗️ Project Structure

```
src/
├── bot.py                        # Main bot entry point
├── config/                       # Configuration & logging
├── data/
│   ├── prompts/                  # AI prompt templates (JSON format)
│   ├── config/                   # Configuration files
│   └── user_summaries/           # User profile data (JSON format)
├── models/                       # Data models (User, Channel, Conversation)
├── services/
│   ├── ai/                       # LLM integrations (Gemini, DeepSeek)
│   ├── channel/                  # Channel management
│   ├── conversation/             # Message processing & anti-spam
│   ├── messeger/                 # Message queue & context building
│   ├── relationship/             # Relationship tracking
│   ├── user/                     # User commands
│   └── user_summary/             # User profiling & summary generation
├── utils/                        # Helper utilities
├── tests/                        # Test suite
└── requirements.txt              # Python dependencies
```

## 🗺️ Architecture

```mermaid
flowchart TB
    subgraph Discord["🎮 Discord"]
        DG[Discord Gateway]
        DC[Discord Channels]
    end

    subgraph Core["🤖 Bot Core"]
        BOT[bot.py<br/>Entry Point]
        LLM_SVC[LLMMessageService<br/>Deduplication]
        MSG_PROC[MessageProcessor<br/>Anti-Spam]
        CONV_MGR[ConversationManager<br/>Per-User Lock]
    end

    subgraph Context["📋 Context Building"]
        CTX[ContextBuilder]
        HIST[HistoryService]
    end

    subgraph Services["⚙️ Business Services"]
        SUM_SVC[SummaryService]
        REL_SVC[RelationshipService]
    end

    subgraph Repository["💾 Repository Layer"]
        SUM_DATA[SummaryDataManager]
        REL_DATA[RelationshipDataManager]
        SUM_PARSE[SummaryParser]
    end

    subgraph AI["🧠 AI Services"]
        GEMINI[GeminiService]
        DEEPSEEK[DeepSeekService]
    end

    subgraph Data["📁 JSON Storage"]
        PROMPTS[(prompts/)]
        SUMMARIES[(user_summaries/)]
        RELATIONS[(relationships/)]
    end

    DG --> BOT
    BOT --> LLM_SVC
    LLM_SVC --> MSG_PROC
    MSG_PROC --> CONV_MGR
    CONV_MGR --> CTX

    CTX --> SUM_SVC
    CTX --> REL_SVC
    CTX --> HIST

    SUM_SVC --> SUM_DATA
    SUM_SVC --> SUM_PARSE
    REL_SVC --> REL_DATA

    SUM_DATA --> SUMMARIES
    REL_DATA --> RELATIONS

    CTX --> GEMINI
    CTX --> DEEPSEEK
    GEMINI --> PROMPTS
    DEEPSEEK --> PROMPTS

    GEMINI --> DC
    DEEPSEEK --> DC

    style Discord fill:#5865F2,color:#fff
    style AI fill:#10a37f,color:#fff
    style Repository fill:#f59e0b,color:#fff
    style Data fill:#6366f1,color:#fff
```

### Message Flow

```text
┌─────────────────┐
│  Discord User   │
│  sends message  │
└────────┬────────┘
         ▼
┌─────────────────┐
│    bot.py       │ ◄── Entry point, auto-discovers Cogs
└────────┬────────┘
         ▼
┌─────────────────┐
│ LLMMessageService│ ◄── Deduplication check
└────────┬────────┘
         ▼
┌─────────────────┐
│ MessageProcessor│ ◄── Anti-spam (5 msg/min)
└────────┬────────┘
         ▼
┌─────────────────────┐
│ ConversationManager │ ◄── Per-user lock (concurrent users OK)
└────────┬────────────┘
         ▼
┌─────────────────┐
│  ContextBuilder │ ◄── Assembles context from:
│                 │     • User Summary (SummaryService)
│                 │     • Relationships (RelationshipService)
│                 │     • Conversation History
└────────┬────────┘
         ▼
┌─────────────────┐
│   AI Service    │ ◄── Gemini / DeepSeek
│  (Generation)   │     Loads prompts from JSON
└────────┬────────┘
         ▼
┌─────────────────┐
│ Typing Simulation│ ◄── Human-like delays
└────────┬────────┘
         ▼
┌─────────────────┐
│ Discord Response│
└─────────────────┘
```

### Design Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Repository** | `SummaryDataManager`, `RelationshipDataManager` | JSON I/O abstraction |
| **Service Layer** | `SummaryService`, `RelationshipService` | Business logic |
| **Parser** | `SummaryParser` | Pure text transformation |
| **Command (Cog)** | `QueueCommands`, `TypingCommands` | Discord commands |
| **Singleton** | `Config` | Centralized configuration |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- Google Gemini API Key (optional, for enhanced AI)
- DeepSeek API Key (optional, for alternative AI)

### Installation Steps

1. **Clone and set up environment:**

   ```bash
   git clone <repository-url>
   cd discord-bot-gemini
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**

   ```env
   DISCORD_LLM_BOT_TOKEN=your_token_here
   GEMINI_API_KEY=your_gemini_key_here
   DEEPSEEK_API_KEY=your_deepseek_key_here
   LLM_MODEL=gemini-2.0-flash
   ENABLE_TYPING_SIMULATION=1
   TYPING_SPEED_WPM=250
   ```

4. **Run the bot:**

   ```bash
   python src/bot.py
   ```

### Optional: Hardware Acceleration

For GPU support, install the appropriate requirements for your hardware:

```bash
# NVIDIA CUDA
pip install -r requirements-gpu-cuda.txt

# AMD ROCm
pip install -r requirements-gpu-rocm.txt

# Intel GPU
pip install -r requirements-gpu-intel.txt

# All optional dependencies
pip install -r requirements-all.txt
```

## 📖 Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `!ping` | Test bot responsiveness |
| `!status` | Check bot status and user info |
| `!relationships [user]` | View user relationships |
| `!conversation user1 user2` | Get conversation summary |
| `!analysis [user]` | AI relationship analysis |
| `!all_users` | Admin: View all users summary |

### Configuration Reference

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `DISCORD_LLM_BOT_TOKEN` | Discord bot token | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `DEEPSEEK_API_KEY` | DeepSeek API key | Optional |
| `LLM_MODEL` | AI model to use | `gemini-2.0-flash` |
| `ENABLE_TYPING_SIMULATION` | Enable typing delays | `1` |
| `TYPING_SPEED_WPM` | Words per minute for typing | `250` |

## 🔧 Development & Testing

### Running Tests

```bash
python -m pytest src/tests -v
```

### Test Suite (67 tests)

| Test File | Coverage |
|-----------|----------|
| `test_summary_data.py` | SummaryDataManager - JSON I/O for user summaries |
| `test_summary_parser.py` | SummaryParser - Text cleaning, parsing, merging |
| `test_relationship_data.py` | RelationshipDataManager - Relationship JSON I/O |
| `test_queue_commands.py` | QueueCommands Cog - Queue status, clear commands |
| `test_typing_commands.py` | TypingCommands Cog - Typing simulation commands |
| `test_prompts.py` | Prompt files - JSON validation, required fields |

All tests passing: `67 passed in 0.72s`

## 🔐 Security & Secret Protection

### Protecting API Keys

1. **`.env` file is git-ignored** - Never commit `.env` to the repository
2. **Pre-commit hooks scan for secrets** - Automatically block commits with API keys
3. **Helper scripts for cleanup** - Remove accidentally tracked files

### Enable Git Hooks

```bash
# Linux / macOS
bash scripts/enable_git_hooks.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\enable_git_hooks.ps1
```

### Check for Tracked Secrets

```bash
# Linux / macOS
bash scripts/check_tracked_sensitive_files.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\check_tracked_sensitive_files.ps1
```

### Remove Accidentally Committed `.env`

```bash
# Linux / macOS
bash scripts/remove_sensitive_files.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\remove_sensitive_files.ps1
```

## 📚 Additional Documentation

- **[BOT_USAGE_GUIDE.md](BOT_USAGE_GUIDE.md)** - User guide for bot interactions
- **[BOT_CHANNELS_GUIDE.md](BOT_CHANNELS_GUIDE.md)** - Channel configuration guide
- **[RELATIONSHIP_GUIDE.md](RELATIONSHIP_GUIDE.md)** - Relationship system guide
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure
- **[TYPING_SIMULATION_GUIDE.md](TYPING_SIMULATION_GUIDE.md)** - Typing simulation details

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- DeepSeek for alternative AI models
- Discord.py for the Discord bot framework
