# filepath: discord-bot-gemini/src/config/settings.py
import os

class Config:
    """
    Configuration class for Discord bot and Gemini API settings.
    All values are loaded from environment variables.
    """
    DISCORD_BOT_TOKEN: str | None = os.getenv('DISCORD_LLM_BOT_TOKEN')
    DISCORD_BOT_CLIENT_ID: str | None = os.getenv('DISCORD_LLM_BOT_CLIENT_ID')
    GEMINI_API_KEY: str | None = os.getenv('GEMINI_API_KEY')
    GEMINI_API_URL: str = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
    SYNC_COMMANDS: str = os.getenv('SYNC_COMMANDS', '0')
    
    # Typing simulation settings
    ENABLE_TYPING_SIMULATION: bool = os.getenv('ENABLE_TYPING_SIMULATION', '1') == '1'
    TYPING_SPEED_WPM: int = int(os.getenv('TYPING_SPEED_WPM', '250'))  # Words per minute
    MIN_TYPING_DELAY: float = float(os.getenv('MIN_TYPING_DELAY', '0.5'))  # Minimum delay in seconds
    MAX_TYPING_DELAY: float = float(os.getenv('MAX_TYPING_DELAY', '8.0'))  # Maximum delay in seconds
    PART_BREAK_DELAY: float = float(os.getenv('PART_BREAK_DELAY', '0.6'))  # Delay between message parts