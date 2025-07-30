import logging

def setup_logging() -> logging.Logger:
    """
    Set up logging configuration for the Discord bot.
    Returns:
        logging.Logger: Configured logger instance for the bot.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    logger = logging.getLogger('discord_bot')
    return logger

logger = setup_logging()