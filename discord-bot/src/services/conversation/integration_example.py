"""
V2.1 Integration Example
Minh họa cách tích hợp các tính năng mới vào bot.py
"""
from src.services.conversation.recent_log_service import recent_log_service
from src.services.conversation.batch_processor import batch_processor
from src.services.conversation.pending_update_service import pending_update_service
from src.utils.helpers import get_logger

logger = get_logger(__name__)


async def handle_message(user_id: str, username: str, content: str, channel_id: str, server_id: str):
    """
    Flow xử lý tin nhắn theo V2.1 Architecture:
    
    1. Check pending updates cho user (Lazy Sync)
    2. Add message vào RecentLog
    3. Check trigger (Batch Full hoặc Time Flush)
    4. Nếu trigger -> Process batch
    """
    
    # STEP 1: Lazy Sync - Check pending updates
    if await pending_update_service.has_pending_updates(user_id, server_id):
        logger.info(f"⚡ User {username} has pending updates, processing...")
        pending_updates = await pending_update_service.get_pending_updates(user_id, server_id)
        
        # TODO: Apply pending updates to user's profile
        # for update in pending_updates:
        #     await apply_relationship_update(user_id, update.data)
        
        # Clear after processing
        await pending_update_service.clear_pending_updates(user_id, server_id)
        logger.info(f"✅ Applied {len(pending_updates)} pending updates for {username}")
    
    # STEP 2: Add message to RecentLog
    should_trigger = await recent_log_service.add_activity(
        user_id=user_id,
        username=username,
        content=content,
        channel_id=channel_id,
        server_id=server_id,
        action="message"
    )
    
    # STEP 3 & 4: Check trigger and process batch
    if should_trigger:
        logger.info("🔔 Batch trigger activated!")
        await batch_processor.process_batch(server_id)
    
    return True


# Example usage in Discord bot
"""
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    await handle_message(
        user_id=str(message.author.id),
        username=message.author.name,
        content=message.content,
        channel_id=str(message.channel.id),
        server_id=str(message.guild.id) if message.guild else "dm"
    )
"""
