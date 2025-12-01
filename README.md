# Discord LLM AI Chatbot

A sophisticated Discord bot powered by Google's Gemini and DeepSeek AI models, featuring intelligent conversation management, relationship tracking, user summaries, and anti-spam protection.

## ✨ Features

### 🤖 AI-Powered Conversations

- **Multi-Model Support**: Integrates Gemini 1.5 Flash and DeepSeek AI for diverse response capabilities
- **Contextual Responses**: Maintains conversation history and user summaries for personalized interactions
- **Typing Simulation**: Realistic typing delays to mimic human-like responses

### 🔗 Intelligent Relationship System

- **Automatic Detection**: Tracks mentions, tags, and relationship statements in conversations
- **Smart Recognition**: Identifies relationships from natural language (e.g., "John and Jane are dating")
- **User Profiling**: Stores real names, usernames, and interaction patterns
- **Conversation Summaries**: AI-generated summaries of user interactions

### 🛡️ Advanced Conversation Management

- **Anti-Spam Protection**: Prevents message flooding with cooldowns
- **Conversation Locking**: Ensures sequential responses per user
- **Message Queuing**: Handles multiple users gracefully
- **Channel Management**: Admin-configurable bot channels

### 📊 User Analytics

- **Personal Summaries**: AI-generated user profiles and conversation summaries
- **Interaction Tracking**: Detailed logs of user engagements
- **Relationship Mapping**: Visual representation of server relationships

## 🏗️ Project Structure

```text

discord-bot-gemini/
├── src/
│   ├── bot.py                    # Main bot entry point with dynamic service loading
│   ├── config/
│   │   ├── settings.py           # Centralized configuration management
│   │   └── logging_config.py     # Logging configuration
│   ├── data/
│   │   ├── prompts/              # AI prompt templates
│   │   │   ├── personality.txt
│   │   │   ├── conversation_prompt.txt
│   │   │   └── server_relationships_prompt.txt
│   │   └── relationships/        # JSON data storage for relationships
│   ├── models/
│   │   ├── user.py              # User data models
│   │   ├── channel.py           # Channel management models
│   │   └── conversation.py      # Conversation data models
│   ├── services/
│   │   ├── ai/
│   │   │   ├── gemini_service.py    # Gemini AI integration
│   │   │   └── deepseek_service.py  # DeepSeek AI integration
│   │   ├── channel/
│   │   │   ├── admin_channels_service.py
│   │   │   └── channel_service.py
│   │   ├── conversation/
│   │   │   ├── conversation_manager.py
│   │   │   ├── history_service.py
│   │   │   ├── message_processor.py
│   │   │   └── anti_spam_service.py
│   │   ├── messeger/
│   │   │   ├── llm_message_service.py
│   │   │   ├── context_builder.py
│   │   │   └── message_queue.py
│   │   ├── relationship/
│   │   │   ├── relationship_service.py
│   │   │   └── relationship_data.py
│   │   ├── user/
│   │   │   └── user_commands.py
│   │   └── user_summary/
│   │       ├── summary_service.py
│   │       ├── summary_data.py
│   │       └── summary_update.py
│   └── utils/
│       └── helpers.py
├── requirements-npu.txt         # NPU support requirements
├── requirements-all.txt         # All requirements combined
├── scripts/
│   └── clean_pycache.py         # Cache cleaning utility
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Gemini API Key (optional, for enhanced AI)
- DeepSeek API Key (optional, for alternative AI)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd discord-bot-gemini
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

   Or use the automated setup script with hardware detection:

   ```bash
   python scripts/setup.py --auto
   ```

3. **Install core dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:

   ```env
   DISCORD_LLM_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_BOT_CLIENT_ID=your_bot_client_id_here
   GEMINI_API_KEY=your_gemini_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here

   # Optional configurations
   LLM_MODEL=gemini-1.5-flash
   ENABLE_TYPING_SIMULATION=1
   TYPING_SPEED_WPM=250
   SYNC_COMMANDS=0
   ```

5. **Run the bot:**

   ```bash
   python src/bot.py
   ```

### Optional Hardware Acceleration

For GPU/NPU support, install additional requirements based on your hardware:

#### NVIDIA CUDA (GPU)

```bash
pip install -r requirements-gpu-cuda.txt
# Requires: CUDA Toolkit installed
```

#### AMD ROCm (GPU)

```bash
pip install -r requirements-gpu-rocm.txt
# Requires: AMD ROCm drivers installed
# Use specific PyTorch wheel for your ROCm version
```

#### Intel GPU

```bash
pip install -r requirements-gpu-intel.txt
# Requires: Intel GPU drivers and oneAPI
```

#### Neural Processing Units (NPU)

```bash
pip install -r requirements-npu.txt
# Supports various NPU implementations via OpenVINO
```

#### Install Everything

```bash
pip install -r requirements-all.txt
# Includes all core + optional dependencies
```

## 📖 Usage

### Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!ping` | Test bot responsiveness | `!ping` |
| `!status` | Check bot status and user info | `!status` |
| `!relationships [user]` | View user relationships | `!relationships @user` |
| `!conversation user1 user2` | Get conversation summary | `!conversation @user1 @user2` |
| `!analysis [user]` | AI relationship analysis | `!analysis @user` |
| `!search_relations keyword` | Search relationships | `!search_relations friend` |
| `!mentions user1 user2` | View mention history | `!mentions @user1 @user2` |
| `!all_users` | Admin: View all users summary | `!all_users` |

### How It Works

1. **Message Processing**: Bot listens for messages in configured channels or DMs
2. **Context Building**: Gathers user history, relationships, and conversation context
3. **AI Generation**: Sends enhanced prompt to Gemini/DeepSeek API
4. **Response Delivery**: Simulates typing and sends response in parts if needed
5. **Data Updates**: Updates user summaries and relationship data

### Configuration Options

- **Bot Channels**: Configure specific channels where bot responds without mentions
- **AI Models**: Switch between Gemini and DeepSeek based on availability
- **Typing Simulation**: Adjust typing speed and delays for realism
- **Anti-Spam**: Configure cooldown periods and message limits

## 🔧 Development

### Adding New Services

1. Create a new service file in `src/services/`
2. Implement `async def setup(bot)` function
3. The bot will automatically load it on startup

### Testing

```bash
# Run unit tests (if available)
pytest

# Test relationship service offline
python test_relationship_service.py
```

### Development Utilities

#### Project Setup Script

```bash
# Automated setup (venv + requirements)
python scripts/setup.py

# Custom setup options
python scripts/setup.py --venv myenv --req requirements-all.txt
python scripts/setup.py --skip-venv  # Only install requirements
```

#### Clean Python Cache

```bash
# Clean __pycache__ directories and .pyc files
python scripts/clean_pycache.py

# Clean specific directory
python scripts/clean_pycache.py /path/to/directory

# Dry run (show what would be cleaned)
python scripts/clean_pycache.py --dry-run
```

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_LLM_BOT_TOKEN` | Discord bot token | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `DEEPSEEK_API_KEY` | DeepSeek API key | Optional |
| `LLM_MODEL` | AI model to use | `gemini-1.5-flash` |
| `ENABLE_TYPING_SIMULATION` | Enable typing delays | `1` |
| `TYPING_SPEED_WPM` | Words per minute for typing | `250` |
| `SYNC_COMMANDS` | Sync slash commands on startup | `0` |

## 📚 Documentation

- **[BOT_USAGE_GUIDE.md](BOT_USAGE_GUIDE.md)** - User guide for bot interactions
- **[BOT_CHANNELS_GUIDE.md](BOT_CHANNELS_GUIDE.md)** - Channel configuration guide
- **[RELATIONSHIP_GUIDE.md](RELATIONSHIP_GUIDE.md)** - Relationship system user guide
- **[RELATIONSHIP_TECHNICAL_DOCS.md](RELATIONSHIP_TECHNICAL_DOCS.md)** - Technical documentation
- **[TYPING_SIMULATION_GUIDE.md](TYPING_SIMULATION_GUIDE.md)** - Typing simulation details
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- DeepSeek for alternative AI model
- Discord.py for the Discord bot framework

## 🗺️ Architecture & Workflow

### High-level Architecture

```mermaid
flowchart LR
   DG[Discord Gateway] --> BotCore[Bot Core\n(bot.py)]
   BotCore --> LLM[LLM Service\n(Gemini / DeepSeek)]
   BotCore --> MQ[Message Queue Manager]
   BotCore --> CB[Context Builder / Summary Service]
   CB --> DB[(JSON Database)]
   MQ --> CB
   LLM --> CB
   CB --> BotCore
   classDef infra fill:#f9f,stroke:#333,stroke-width:1px;
   class DG,DB infra;
```

### Security & Preventing Secret Leaks

1. NEVER commit `.env` or real API keys to git. Use `.env.example` to store variable names only.
1. `.gitignore` has been updated to include `.env`, logs, venv and user data directories.
1. There is a pre-commit hook in `.githooks/` that scans staged files for common secret patterns. To enable it locally:

```bash
git config core.hooksPath .githooks
```

1. If a secret is committed accidentally:

```bash
# Remove it from the index
git rm --cached .env
git commit -m "chore: remove .env from repo"
git push origin main

# To purge from history (dangerous):
# bfg --delete-files .env
# git reflog expire --expire=now --all && git gc --prune=now --aggressive
# git push --force
```

1. Rotate compromised keys immediately.

### Quick checks & automation

Run a quick check to see if any sensitive files are tracked by git:

#
```bash
# Linux / macOS
bash scripts/check_tracked_sensitive_files.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\check_tracked_sensitive_files.ps1
```

## ✅ Enable Git Hooks and Secret Protection (Recommended)

To enable the included pre-commit hooks that scan for secrets, run one of the following:

```bash
# Linux / macOS
bash scripts/enable_git_hooks.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\enable_git_hooks.ps1
```

To remove accidentally committed `.env` from the index and commit the removal (safe, local only):

```bash
# Linux / macOS
bash scripts/remove_sensitive_files.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\remove_sensitive_files.ps1
```


