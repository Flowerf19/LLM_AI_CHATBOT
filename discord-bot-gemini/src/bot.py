import os
import sys
import discord
from discord.ext import commands
from config.settings import Config
from config.logging_config import setup_logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)



# Configure logging
logger = setup_logging()

class DiscordBot(commands.Bot):
    """
    Main Bot class that handles initialization, service loading, and event handling.
    Follows Singleton pattern implicitly as the main application entry point.
    """
    
    def __init__(self):
        # Initialize Intents
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
            max_messages=500
        )
        
    async def setup_hook(self):
        """
        Async setup hook called before the bot starts.
        Used for loading extensions and syncing commands.
        """
        logger.info("🚀 Initializing Discord Bot...")
        
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.critical(f"❌ Configuration Error: {e}")
            await self.close()
            return

        # Load services
        await self.load_services()
        
        # Sync commands if enabled
        if Config.SYNC_COMMANDS:
            try:
                synced = await self.tree.sync()
                logger.info(f"✅ Synced {len(synced)} slash commands")
            except Exception as e:
                logger.warning(f"⚠️ Slash command sync failed: {e}")

    async def load_services(self):
        """Dynamically load all service modules that have a setup function"""
        services_dir = Config.SRC_DIR / 'services'
        
        if not services_dir.exists():
            logger.warning(f"⚠️ Services directory not found: {services_dir}")
            return

        count = 0
        # Walk through services directory
        for path in services_dir.rglob('*.py'):
            if path.name.startswith('__'):
                continue
                
            # Convert file path to module path
            # e.g. src/services/ai/gemini_service.py -> services.ai.gemini_service
            try:
                relative_path = path.relative_to(Config.SRC_DIR)
                module_path = str(relative_path).replace(os.sep, '.')[:-3]
                
                await self.load_extension(module_path)
                logger.info(f"✅ Loaded service: {module_path}")
                count += 1
            except commands.NoEntryPointError:
                # Skip files without setup() function
                pass 
            except Exception as e:
                logger.error(f"❌ Failed to load service {module_path}: {e}")

        if count == 0:
            logger.warning("⚠️ No services loaded!")
        else:
            logger.info(f"✨ Successfully loaded {count} services")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'🚀 Bot started as {self.user} in {len(self.guilds)} guilds')

    async def on_error(self, event_method, *args, **kwargs):
        """Global error handler"""
        logger.error(f"❌ Unhandled error in {event_method}", exc_info=True)

def main():
    """Entry point"""
    bot = DiscordBot()
    
    if not Config.DISCORD_BOT_TOKEN:
        logger.critical("❌ Bot token not found! Please check your .env file.")
        return

    try:
        bot.run(Config.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
