"""
MessageProcessor - Main entry point for Discord message handling
V2.1: Integrated with Lazy Sync and Batch Processing
"""
import discord
import asyncio
from src.utils.helpers import get_logger
from src.services.conversation.recent_log_service import recent_log_service
from src.services.conversation.anti_spam_service import AntiSpamService
from src.services.conversation.pending_update_service import pending_update_service
from src.services.messeger.llm_message_service import LLMMessageService
from src.services.conversation.batch_processor import batch_processor

logger = get_logger(__name__)

class MessageProcessor:
    def __init__(self, bot):
        self.bot = bot
        self.anti_spam = AntiSpamService()
        self.llm_service = LLMMessageService(bot)

    async def process_message(self, message: discord.Message):
        """
        Main entry point for processing new messages.
        V2.1 Flow:
        1. Validation & Anti-spam
        2. Check & Apply Pending Updates (Lazy Sync)
        3. Save to RecentLog (Sliding Window)
        4. Check Trigger (Batch Full or Time Flush)
        5. Trigger Batch AI (Background Task if needed)
        6. Reply to User (Immediate)
        """
        # 1. Validation
        if message.author.bot:
            return
        
        # Lấy thông tin Server ID (Handle DM vs Guild)
        server_id = str(message.guild.id) if message.guild else "dm_channel"
        channel_id = str(message.channel.id)
        user_id = str(message.author.id)
        username = message.author.name
        
        # Check spam
        is_spam, cooldown = self.anti_spam.check_spam(user_id)
        if is_spam:
            logger.warning(f"Spam detected from {username}, cooldown: {cooldown}s")
            return

        # 2. V2.1 - Lazy Sync: Check pending updates for this user
        await self._check_and_apply_pending_updates(user_id, username, server_id)

        # 3. Save to RecentLog (V2.1 Logic with Hybrid Trigger)
        mentioned_users = [str(u.id) for u in message.mentions]
        
        should_trigger_batch = await recent_log_service.add_activity(
            user_id=user_id,
            username=username,
            content=message.content,
            channel_id=channel_id,
            server_id=server_id,
            action="message",
            mentioned_users=mentioned_users
        )

        # 4 & 5. Trigger Batch AI if needed (Background task)
        if should_trigger_batch:
            logger.info("⚡ Batch Trigger Activated (10 msgs or 30 min timeout)")
            asyncio.create_task(self._run_batch_processing(server_id))

        # 6. Reply to User (Immediate Response)
        if self.should_reply(message):
            await self._handle_bot_response(message)

    async def _check_and_apply_pending_updates(self, user_id: str, username: str, server_id: str):
        """
        V2.1 - Lazy Sync: Check if user has pending updates and apply them.
        This happens when User A had an event affecting User B while B was offline.
        """
        try:
            if await pending_update_service.has_pending_updates(user_id, server_id):
                pending_updates = await pending_update_service.get_pending_updates(user_id, server_id)
                
                logger.info(f"⚡ Applying {len(pending_updates)} pending updates for {username}")
                
                # TODO: Apply each pending update to user's profile
                # For now, we'll just log them. In Phase 2, implement actual update logic:
                # - Load user's UserSummary
                # - Merge relationship data from pending updates
                # - Save updated summary
                
                for update in pending_updates:
                    logger.debug(f"  - {update.update_type}: {update.data}")
                
                # Clear after processing
                await pending_update_service.clear_pending_updates(user_id, server_id)
                logger.info(f"✅ Applied pending updates for {username}")
                
        except Exception as e:
            logger.error(f"Error applying pending updates for {username}: {e}")

    async def _run_batch_processing(self, server_id: str = "default"):
        """
        V2.1 - Run batch processing with full integration.
        Calls BatchProcessor to analyze recent messages.
        """
        try:
            logger.info("🔄 Starting Batch Processing...")
            
            # Call the actual batch processor
            await batch_processor.process_batch(server_id)
            
            logger.info("✅ Batch Processing Completed")
            
        except Exception as e:
            logger.error(f"❌ Error in batch processing: {e}", exc_info=True)
            # Still reset tracker to avoid getting stuck
            await recent_log_service.reset_batch_tracker()

    async def _handle_bot_response(self, message: discord.Message):
        """
        Xử lý việc bot trả lời người dùng.
        """
        async with message.channel.typing():
            # Lấy context từ Sliding Window (RAM/RecentLog) thay vì đọc file history cũ
            # Lấy 20 tin gần nhất để làm short-term memory cho câu trả lời
            recent_context = await recent_log_service.get_recent_context(limit=20)
            
            # Gọi LLM Service để sinh câu trả lời
            # Lưu ý: LLMMessageService cần được update để nhận raw context string nếu chưa hỗ trợ
            response_text = await self.llm_service.generate_response(
                user_message=message.content,
                context=recent_context,
                user_id=str(message.author.id)
            )

            if response_text:
                await message.channel.send(response_text)

    def should_reply(self, message: discord.Message) -> bool:
        """
        Logic quyết định bot có trả lời tin nhắn này không.
        """
        # Ví dụ: Trả lời khi được mention hoặc chat trong DM
        is_mentioned = self.bot.user in message.mentions
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_reply_to_bot = (message.reference and 
                           message.reference.resolved and 
                           message.reference.resolved.author == self.bot.user)

        return is_mentioned or is_dm or is_reply_to_bot