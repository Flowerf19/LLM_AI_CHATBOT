import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import asyncio
# Import AdminChannelsService for setup
from services.channel.admin_channels_service import AdminChannelsService

# Add project root to path for importing services
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

# Simplified logging configuration
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Simplified format
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('discord_bot')

logger.info("🚀 Starting Discord Bot...")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True,
    strip_after_prefix=True,
    max_messages=500
)

@bot.event
async def on_ready():
    logger.info(f'🚀 Bot started as {bot.user} in {len(bot.guilds)} guilds')
    
    if os.getenv('SYNC_COMMANDS') == '1':
        try:
            await bot.tree.sync()
            logger.info("✅ Slash commands synced")
        except Exception as e:
            logger.warning(f"⚠️ Slash command sync failed: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"❌ Unhandled error in {event}", exc_info=True)

async def load_services():
    """Load all services from services directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    services_dir = os.path.join(current_dir, 'services')
    
    if not os.path.exists(services_dir):
        logger.warning(f"⚠️ Services directory not found: {services_dir}")
        return
    
    # Tìm tất cả file .py trong services và subfolder
    # Chỉ load các file có hàm setup(bot)
    import ast
    service_files = []
    for root, dirs, files in os.walk(services_dir):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                try:
                    tree = ast.parse(source)
                    has_setup = any(
                        isinstance(node, ast.AsyncFunctionDef) and node.name == 'setup'
                        for node in tree.body
                    )
                except Exception:
                    has_setup = False
                if has_setup:
                    rel_path = os.path.relpath(file_path, services_dir)
                    module_path = rel_path.replace('\\', '.').replace('/', '.')
                    module_name = f"services.{module_path[:-3]}"
                    service_files.append(module_name)

    if not service_files:
        logger.warning("⚠️ No service files found with setup(bot)")
        return

    loaded = 0
    for service in service_files:
        try:
            await bot.load_extension(service)
            loaded += 1
            logger.info(f"✅ Loaded {service}")
        except Exception as e:
            logger.error(f"❌ Failed to load service {service}: {e}")

    logger.info(f"📦 Loaded {loaded}/{len(service_files)} services")

async def main():
    try:
        async with bot:
            await load_services()
            
            token = os.getenv('DISCORD_LLM_BOT_TOKEN')
            if not token:
                logger.error("❌ No Discord token found in environment")
                return
                
            await bot.start(token)
            
    except discord.LoginFailure:
        logger.error("❌ Invalid Discord token")
    except Exception as e:
        logger.error(f"❌ Bot startup failed: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()
        logger.info("🔒 Bot shutdown complete")

async def setup(bot):
    await bot.add_cog(AdminChannelsService(bot))
    try:
        await bot.tree.sync()  # Sync tất cả slash commands lên server
        print("✅ Slash commands synced!")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")