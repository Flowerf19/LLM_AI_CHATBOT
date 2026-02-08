import logging
import discord

logger = logging.getLogger("discord_bot.ContextBuilder")


class ContextBuilder:
    def __init__(self, bot, summary_service, relationship_service):
        self.bot = bot
        self.summary_service = summary_service
        self.relationship_service = relationship_service
        # Cache parsed summary JSON: {user_id: (parsed_dict, raw_summary)}
        self._parsed_summary_cache: dict = {}

    def should_respond_to_message(self, message) -> bool:
        """Determine if bot should respond to message"""
        if isinstance(message.channel, discord.DMChannel):
            return True
        if hasattr(message, "guild") and message.guild:
            is_mentioned = self.bot.user.mentioned_in(message)
            admin_service = self.bot.get_cog("AdminChannelsService")
            is_bot_channel = (
                admin_service.is_bot_channel(message.guild.id, message.channel.id)
                if admin_service
                else True
            )
            return is_mentioned or is_bot_channel
        return False

    def clean_message_content(self, message) -> str:
        """Remove bot mentions from message content"""
        content = message.content
        if self.bot.user.mentioned_in(message):
            content = content.replace(f"<@{self.bot.user.id}>", "").strip()
            content = content.replace(f"<@!{self.bot.user.id}>", "").strip()
        return content

    def build_enhanced_context(
        self, user_id: str, user_summary: str, mentioned_users_info: str, context: str
    ) -> str:
        """Build enhanced context for AI"""
        enhanced_context = ""

        # Check if we know the user's real name
        real_name_known = False
        discord_name = self.relationship_service.get_user_display_name(user_id)

        if user_summary:
            enhanced_context += f"=== NGƯỜI ĐANG NÓI CHUYỆN (USER ID: {user_id}) ===\n{user_summary}\n\n"

            # Use cached parsed JSON or parse and cache
            summary_data = self._get_parsed_summary(user_id, user_summary)
            if summary_data:
                basic_info = summary_data.get("basic_info", {})
                name = basic_info.get("name", "Không có")
                if name and name.lower() not in [
                    "không có",
                    "unknown",
                    "chưa biết",
                    "chưa tiết lộ",
                ]:
                    real_name_known = True

        # If real name is unknown, instruct bot to use Discord display name
        if not real_name_known:
            enhanced_context += f'=== LƯU Ý QUAN TRỌNG ===\nNgười dùng chưa cho biết tên thật.\nHÃY GỌI HỌ LÀ: "{discord_name}" (đây là tên hiển thị của họ).\n\n'

        try:
            user_display_name = self.relationship_service.get_user_display_name(user_id)
            user_relationships = self.relationship_service.get_user_relationships(
                user_id
            )
            interaction_stats = self.relationship_service.get_interaction_stats(user_id)
            if user_relationships or interaction_stats.get("total_interactions", 0) > 0:
                enhanced_context += (
                    f"=== MỐI QUAN HỆ VÀ TƯƠNG TÁC CỦA {user_display_name} ===\n"
                )
                if user_relationships:
                    enhanced_context += "Mối quan hệ:\n"
                    for rel in user_relationships[:5]:
                        enhanced_context += (
                            f"- {rel['other_person']}: {rel['relationship_type']}\n"
                        )
                if interaction_stats.get("top_contacts"):
                    enhanced_context += "\nNgười liên lạc thường xuyên:\n"
                    for contact in interaction_stats["top_contacts"][:3]:
                        enhanced_context += f"- {contact['name']}: {contact['interaction_count']} lần tương tác\n"
                enhanced_context += "\n"
        except Exception as e:
            logger.error(f"Error getting relationship context: {e}")
        if mentioned_users_info:
            enhanced_context += (
                f"=== THÔNG TIN VỀ NGƯỜI ĐƯỢC NHẮC ĐẾN ===\n{mentioned_users_info}\n\n"
            )
        if context:
            enhanced_context += (
                f"=== LỊCH SỬ HỘI THOẠI CỦA NGƯỜI HIỆN TẠI ===\n{context}\n\n"
            )
        enhanced_context += f"=== QUAN TRỌNG ===\nBạn đang nói chuyện với USER ID {user_id}. Đừng nhầm lẫn với những người khác được nhắc đến trong tin nhắn."
        return enhanced_context

    def _get_parsed_summary(self, user_id: str, user_summary: str) -> dict | None:
        """Get parsed summary from cache or parse and cache it"""
        import json

        # Check cache - invalidate if raw summary changed
        if user_id in self._parsed_summary_cache:
            cached_data, cached_raw = self._parsed_summary_cache[user_id]
            if cached_raw == user_summary:
                return cached_data

        # Parse and cache
        try:
            parsed = json.loads(user_summary)
            self._parsed_summary_cache[user_id] = (parsed, user_summary)
            return parsed
        except Exception:
            return None

    def get_mentioned_users_info(self, content: str, message=None) -> str:
        """Get information about mentioned users, prefer display name/nickname over ID"""
        import re

        user_mentions = re.findall(r"<@!?(\d+)>", content)
        if not user_mentions:
            return ""
        mentioned_info_parts = []
        mention_name_map = {}
        if message and hasattr(message, "mentions"):
            for m in message.mentions:
                display = (
                    getattr(m, "global_name", None)
                    or getattr(m, "display_name", None)
                    or getattr(m, "name", None)
                    or str(m.id)
                )
                mention_name_map[str(m.id)] = display
        for mentioned_user_id in user_mentions:
            display_name = mention_name_map.get(mentioned_user_id)
            if not display_name and hasattr(self, "relationship_service"):
                display_name = self.relationship_service.get_user_display_name(
                    mentioned_user_id
                )
            if not display_name:
                display_name = mentioned_user_id
            try:
                mentioned_user_summary = self.summary_service.get_user_summary(
                    mentioned_user_id
                )
                if mentioned_user_summary:
                    mentioned_info_parts.append(
                        f"{display_name} (ID: {mentioned_user_id}):\n{mentioned_user_summary}"
                    )
                else:
                    mentioned_info_parts.append(
                        f"{display_name} (ID: {mentioned_user_id}): Chưa có thông tin"
                    )
            except Exception as e:
                logger.error(
                    f"Error getting info for mentioned user {mentioned_user_id}: {e}"
                )
        return "\n\n".join(mentioned_info_parts) if mentioned_info_parts else ""
