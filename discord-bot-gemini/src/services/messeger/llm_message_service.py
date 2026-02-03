import logging
from discord.ext import commands
from services.ai.gemini_service import GeminiService
from services.ai.ollama_service import OllamaService
from services.messeger.message_queue import MessageQueueManager
from services.messeger.context_builder import ContextBuilder
from services.relationship.relationship_service import RelationshipService
from services.user_summary.summary_service import SummaryService
from config.settings import Config
import re

logger = logging.getLogger('discord_bot.LLMMessageService')

class LLMMessageService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Initialize AI services
        self.ollama_service = OllamaService()
        self.gemini_service = GeminiService() if Config.USE_OLLAMA_BACKUP else None
        
        # Use Ollama as primary service for summaries/relationships
        self.summary_service = SummaryService(self.ollama_service)
        self.relationship_service = RelationshipService(self.ollama_service)
        self.queue_manager = MessageQueueManager()
        self.context_builder = ContextBuilder(bot, self.summary_service, self.relationship_service)
        self._processed_message_ids = set()  # Dùng set để lưu các message đã xử lý
        
        if self.gemini_service:
            logger.info("🤖 LLMMessageService initialized with Ollama (primary) + Gemini (backup)")
        else:
            logger.info("🤖 LLMMessageService initialized with Ollama only")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        # Chỉ xử lý nếu chưa xử lý message này
        if message.id in self._processed_message_ids:
            return
        self._processed_message_ids.add(message.id)
        # Nếu là lệnh command (! hoặc /), bỏ qua - discord.py tự động xử lý commands
        if message.content and (message.content.startswith('!') or message.content.startswith('/')):
            # KHÔNG gọi process_commands() ở đây - discord.py đã tự động gọi rồi
            return
        # Nếu không phải lệnh, chỉ xử lý AI nếu should_process_message
        if not await self.queue_manager.message_processor.should_process_message(message):
            return
        await self.queue_manager.message_processor.process_with_lock(message, self._handle_message)

    async def _handle_message(self, message):
        if message.content.startswith('!') or message.content.startswith('/'):
            return
        if not self.context_builder.should_respond_to_message(message):
            return
        content = self.context_builder.clean_message_content(message)
        if not content.strip():
            return
        user_id = str(message.author.id)
        await self._process_relationship_data(message, content, user_id)
        is_spam, cooldown_remaining = self.queue_manager.is_spam(user_id)
        if is_spam:
            spam_msg = f"🚫 **Anti-Spam**: Bạn đang gửi tin nhắn quá nhanh! Vui lòng đợi {cooldown_remaining}s."
            await message.reply(spam_msg)
            return
        if self.queue_manager.is_conversation_locked(user_id):
            duration = self.queue_manager.get_lock_duration(user_id)
            busy_msg = f"⏳ Tôi đang xử lý tin nhắn trước của bạn ({duration}s). Xin đợi một chút nhé!"
            await message.reply(busy_msg)
            self.queue_manager.add_to_pending_queue(message, content)
            return
        await self._process_ai_response(message, content, user_id)

    async def _process_ai_response(self, message, content: str, user_id: str):
        response_sent = False
        try:
            self.queue_manager.set_conversation_lock(user_id)
            context = self.queue_manager.get_conversation_context(user_id)
            user_summary = self.summary_service.get_user_summary(user_id)
            mentioned_users_info = self.context_builder.get_mentioned_users_info(content, message)
            enhanced_context = self.context_builder.build_enhanced_context(user_id, user_summary, mentioned_users_info, context)
            
            async with message.channel.typing():
                # Try Ollama first, fallback to Gemini if enabled
                response = None
                try:
                    response = await self.ollama_service.generate_response(content, user_id, enhanced_context)
                except Exception as ollama_error:
                    logger.warning(f"⚠️ Ollama error: {ollama_error}")
                    if self.gemini_service:
                        logger.info("✨ Falling back to Gemini...")
                        try:
                            response = await self.gemini_service.generate_response(content, user_id, enhanced_context)
                        except Exception as gemini_error:
                            logger.error(f"❌ Gemini also failed: {gemini_error}")
                
                if response and len(response.strip()) > 0:
                    await self.send_response_in_parts(message, response, user_id)
                    response_sent = True
                    self.queue_manager.add_to_history(user_id, content, response)
                    self.queue_manager.save_to_persistent_history(user_id, content, response)
                    self.summary_service.increment_message_count(user_id)
                    if self.summary_service.should_update_summary(user_id):
                        try:
                            await self.summary_service.update_summary_smart(user_id, self.ollama_service)
                        except Exception as e:
                            logger.error(f"❌ Error updating summary for {user_id}: {e}")
                else:
                    await message.reply("Xin lỗi, tôi không thể tạo phản hồi cho tin nhắn này.")
                    response_sent = True
        except Exception as e:
            logger.error(f"❌ Error processing AI response: {e}")
            if not response_sent:
                await message.reply("Xin lỗi, đã có lỗi xảy ra khi tạo phản hồi.")
        finally:
            self.queue_manager.release_conversation_lock(user_id)

    async def send_response_in_parts(self, message, response: str, user_id: str):
        """Send response with realistic typing simulation"""
        import random
        import asyncio
        
        # Check if typing simulation is enabled
        if not Config.ENABLE_TYPING_SIMULATION:
            # Send response normally without typing effect
            if len(response) <= 2000:
                await message.reply(response)
                return
            # Fall back to simple splitting for long messages
            parts = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for i, part in enumerate(parts):
                if i == 0:
                    await message.reply(part)
                else:
                    await message.channel.send(part)
            return
        
        # Split response into sentences/parts
        response_parts = self._split_response_naturally(response)
        
        # Send each part with typing simulation
        for i, part in enumerate(response_parts):
            if not part.strip():
                continue
            
            # Show typing indicator
            async with message.channel.typing():
                # Realistic typing delay based on message length
                typing_delay = self._calculate_typing_delay(part)
                await asyncio.sleep(typing_delay)
            
            # Send the message
            if i == 0:
                await message.reply(part)
            else:
                await message.channel.send(part)
            
            # Short pause between messages (except for last one)
            if i < len(response_parts) - 1:
                await asyncio.sleep(random.uniform(0.3, Config.PART_BREAK_DELAY))
    
    def _split_response_naturally(self, response: str) -> list:
        """
        Split response into natural parts: mỗi câu là một phần, xuống dòng đúng dấu câu.
        Hỗ trợ các dấu: . ! ? … ~ (và các dấu kết câu tiếng Việt phổ biến)
        """
        import re

        response = response.strip()
        if not response:
            return []

        # Regex: tách theo dấu kết câu, giữ lại dấu và khoảng trắng phía sau
        # Bao gồm: . ! ? … ~ và các dấu câu unicode
        sentence_end_re = re.compile(r'([^.!?…~]+[.!?…~]+[\s\n]*)', re.UNICODE)
        parts = sentence_end_re.findall(response)

        # Nếu còn phần dư (không kết thúc bằng dấu câu), thêm vào cuối
        consumed = ''.join(parts)
        if len(consumed) < len(response):
            parts.append(response[len(consumed):].strip())

        # Loại bỏ phần rỗng và strip từng phần
        return [p.strip() for p in parts if p.strip()]
    
    def _calculate_typing_delay(self, text: str) -> float:
        """Calculate realistic typing delay based on text length and complexity"""
        import random
        
        # Convert WPM to characters per second (average 5 chars per word)
        chars_per_second = (Config.TYPING_SPEED_WPM * 5) / 60
        
        # Add some variation for realistic feel
        chars_per_second *= random.uniform(0.8, 1.2)
        
        # Adjust for text complexity
        complexity_factors = {
            'emoji': len([c for c in text if ord(c) > 127]) * 0.2,  # Emoji/unicode slow down
            'punctuation': len([c for c in text if c in '.,!?;:']) * 0.1,  # Punctuation pause
            'spaces': text.count(' ') * 0.05,  # Word boundaries
            'thinking': 0.5 if any(word in text.lower() for word in ['hmm', 'ờm', 'à', 'ủa']) else 0
        }
        
        # Calculate base delay
        text_length = len(text)
        base_delay = text_length / chars_per_second
        
        # Add complexity delays
        complexity_delay = sum(complexity_factors.values())
        
        # Add some randomness for natural feel
        random_factor = random.uniform(0.8, 1.3)
        
        # Final delay with reasonable bounds
        total_delay = (base_delay + complexity_delay) * random_factor
        
        # Ensure delay is within configured bounds
        return max(Config.MIN_TYPING_DELAY, min(Config.MAX_TYPING_DELAY, total_delay))

    async def _process_relationship_data(self, message, content: str, user_id: str):
        """Process relationship data from message"""
        try:
            # Get author info
            author_username = message.author.display_name or message.author.name
            message.author.global_name if hasattr(message.author, 'global_name') else None
            
            # Extract mentioned users
            mentioned_user_ids = []
            for mention in message.mentions:
                mentioned_user_ids.append(str(mention.id))
                # Update mentioned user's name info too
                self.relationship_service.update_user_name(
                    str(mention.id), 
                    mention.display_name or mention.name,
                    mention.display_name if mention.display_name != mention.name else None,
                    mention.global_name if hasattr(mention, 'global_name') else None
                )
            
            # Extract real names from message content if user mentions them
            # Pattern để detect khi user nói về tên thật của ai đó
            name_patterns = [
                r'tên\s+(tôi|mình|em)\s+(?:là\s+)?(\w+)',  # "tên tôi là X"
                r'(?:tôi|mình|em)\s+tên\s+(?:là\s+)?(\w+)',  # "tôi tên X"
                r'(?:gọi|call)\s+(?:tôi|mình|em)\s+(?:là\s+)?(\w+)',  # "gọi tôi là X"
                r'(\w+)\s+tên\s+(?:thật\s+)?(?:là\s+)?(\w+)',  # "A tên thật là B"
            ]
            
            for pattern in name_patterns:
                matches = re.finditer(pattern, content.lower())
                for match in matches:
                    if len(match.groups()) == 2:
                        # Case: "A tên là B"
                        person_ref, real_name = match.groups()
                        if person_ref in ['tôi', 'mình', 'em']:
                            # User talking about themselves
                            self.relationship_service.update_user_name(
                                user_id, 
                                author_username, 
                                author_username,
                                real_name.title()
                            )
                    elif len(match.groups()) == 1:
                        # Case: "tôi tên X"
                        real_name = match.groups()[0]
                        self.relationship_service.update_user_name(
                            user_id, 
                            author_username, 
                            author_username,
                            real_name.title()
                        )
            
            # Process the message through relationship service
            self.relationship_service.process_message(
                user_id,
                author_username,
                content,
                mentioned_user_ids,
                str(message.channel.id) if message.channel else None
            )
            
            logger.debug(f"🔗 Processed relationship data for {author_username} (ID: {user_id})")
            
        except Exception as e:
            logger.error(f"❌ Error processing relationship data: {e}")


async def setup(bot):
    await bot.add_cog(LLMMessageService(bot))
