# filepath: discord-bot-gemini/src/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

class Config:
    """
    Central configuration class for the application.
    Manages environment variables and file paths.
    """
    
    # =========================================================================
    # PATH CONFIGURATION
    # =========================================================================
    # Base paths
    SRC_DIR = Path(__file__).parent.parent
    ROOT_DIR = SRC_DIR.parent
    
    # Data paths
    DATA_DIR = SRC_DIR / "data"
    PROMPTS_DIR = DATA_DIR / "prompts"
    USER_SUMMARIES_DIR = DATA_DIR / "user_summaries"
    
    # Log paths
    LOG_FILE = ROOT_DIR / "bot.log"

    # =========================================================================
    # BOT CONFIGURATION
    # =========================================================================
    DISCORD_BOT_TOKEN: str | None = os.getenv('DISCORD_LLM_BOT_TOKEN')
    DISCORD_BOT_CLIENT_ID: str | None = os.getenv('DISCORD_LLM_BOT_CLIENT_ID')
    SYNC_COMMANDS: bool = os.getenv('SYNC_COMMANDS', '0') == '1'

    # =========================================================================
    # AI CONFIGURATION
    # =========================================================================
    # Gemini (Primary)
    GEMINI_API_KEY: str | None = os.getenv('GEMINI_API_KEY')
    GEMINI_API_URL: str = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.0-flash')
    
    # Ollama (Backup/Local)
    OLLAMA_API_URL: str = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'qwen3:1.7b')
    USE_OLLAMA_BACKUP: bool = os.getenv('USE_OLLAMA_BACKUP', '1') == '1'  # Use Ollama as backup

    # =========================================================================
    # TYPING SIMULATION
    # =========================================================================
    ENABLE_TYPING_SIMULATION: bool = os.getenv('ENABLE_TYPING_SIMULATION', '1') == '1'
    TYPING_SPEED_WPM: int = int(os.getenv('TYPING_SPEED_WPM', '250'))
    MIN_TYPING_DELAY: float = float(os.getenv('MIN_TYPING_DELAY', '0.5'))
    MAX_TYPING_DELAY: float = float(os.getenv('MAX_TYPING_DELAY', '8.0'))
    PART_BREAK_DELAY: float = float(os.getenv('PART_BREAK_DELAY', '0.6'))

    # =========================================================================
    # CONVERSATION CONFIGURATION
    # =========================================================================
    MAX_HISTORY_LENGTH: int = int(os.getenv('MAX_HISTORY_LENGTH', '50'))

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("Missing DISCORD_LLM_BOT_TOKEN in environment variables")
        if not cls.GEMINI_API_KEY and not cls.USE_OLLAMA_BACKUP:
            raise ValueError("Missing GEMINI_API_KEY and Ollama backup is disabled")
