import logging
import discord

logger = logging.getLogger('discord_bot.ContextBuilder')

class ContextBuilder:
    def __init__(self, bot, summary_service, relationship_service):
        self.bot = bot
        self.summary_service = summary_service  # Can be None now
        self.relationship_service = relationship_service  # Can be None now

    def should_respond_to_message(self, message) -> bool:
        """Determine if bot should respond to message"""
        if isinstance(message.channel, discord.DMChannel):
            return True
        if hasattr(message, 'guild') and message.guild:
            is_mentioned = self.bot.user.mentioned_in(message)
            admin_service = self.bot.get_cog('AdminChannelsService')
            is_bot_channel = admin_service.is_bot_channel(message.guild.id, message.channel.id) if admin_service else True
            return is_mentioned or is_bot_channel
        return False

    def clean_message_content(self, message) -> str:
        """Remove bot mentions from message content"""
        content = message.content
        if self.bot.user.mentioned_in(message):
            content = content.replace(f'<@{self.bot.user.id}>', '').strip()
            content = content.replace(f'<@!{self.bot.user.id}>', '').strip()
        return content

    def build_enhanced_context(self, user_id: str, user_summary: str, mentioned_users_info: str, context: str) -> str:
        """Build enhanced context for AI"""
        enhanced_context = ""
        if user_summary:
            enhanced_context += f"=== NGƯỜI ĐANG NÓI CHUYỆN (USER ID: {user_id}) ===\n{user_summary}\n\n"
        
        # Simplified without relationship service
        if mentioned_users_info:
            enhanced_context += f"=== THÔNG TIN VỀ NGƯỜI ĐƯỢC NHẮC ĐẾN ===\n{mentioned_users_info}\n\n"
        if context:
            enhanced_context += f"=== LỊCH SỬ HỘI THOẠI CỦA NGƯỜI HIỆN TẠI ===\n{context}\n\n"
        enhanced_context += f"=== QUAN TRỌNG ===\nBạn đang nói chuyện với USER ID {user_id}. Đừng nhầm lẫn với những người khác được nhắc đến trong tin nhắn."
        return enhanced_context

    def get_mentioned_users_info(self, content: str, message=None) -> str:
        """Get information about mentioned users, prefer display name/nickname over ID"""
        import re
        user_mentions = re.findall(r'<@!?(\d+)>', content)
        if not user_mentions:
            return ""
        mentioned_info_parts = []
        mention_name_map = {}
        if message and hasattr(message, "mentions"):
            for m in message.mentions:
                display = getattr(m, "global_name", None) or getattr(m, "display_name", None) or getattr(m, "name", None) or str(m.id)
                mention_name_map[str(m.id)] = display
        for mentioned_user_id in user_mentions:
            display_name = mention_name_map.get(mentioned_user_id)
            if not display_name and self.relationship_service:
                display_name = self.relationship_service.get_user_display_name(mentioned_user_id)
            if not display_name:
                display_name = mentioned_user_id
            try:
                if self.summary_service:
                    mentioned_user_summary = self.summary_service.get_user_summary(mentioned_user_id)
                    if mentioned_user_summary:
                        mentioned_info_parts.append(f"{display_name} (ID: {mentioned_user_id}):\n{mentioned_user_summary}")
                    else:
                        mentioned_info_parts.append(f"{display_name} (ID: {mentioned_user_id}): Chưa có thông tin")
                else:
                    mentioned_info_parts.append(f"{display_name} (ID: {mentioned_user_id}): Thông tin không khả dụng")
            except Exception as e:
                logger.error(f"Error getting info for mentioned user {mentioned_user_id}: {e}")
        return "\n\n".join(mentioned_info_parts) if mentioned_info_parts else "" 