import logging
from services.conversation.conversation_manager import ConversationManager
from services.conversation.anti_spam_service import AntiSpamService
from services.conversation.message_processor import MessageProcessor
from config.settings import Config
import discord

logger = logging.getLogger('discord_bot.MessageQueue')

class MessageQueueManager:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.anti_spam = AntiSpamService()
        self.message_processor = MessageProcessor()

    def is_spam(self, user_id: str):
        return self.anti_spam.check_spam(user_id)

    def is_conversation_locked(self, user_id: str):
        return self.conversation_manager.is_conversation_locked(user_id)

    def get_lock_duration(self):
        return self.conversation_manager.get_lock_duration()

    def add_to_pending_queue(self, message, content):
        self.conversation_manager.add_to_pending_queue(message, content)

    def set_conversation_lock(self, user_id: str):
        self.conversation_manager.set_conversation_lock(user_id)

    def release_conversation_lock(self):
        self.conversation_manager.release_conversation_lock()

    def add_to_history(self, user_id: str, content: str, response: str):
        self.conversation_manager.add_to_history(user_id, content, response)

    def save_to_persistent_history(self, user_id: str, content: str, response: str):
        self.conversation_manager.save_to_persistent_history(user_id, content, response)

    def get_conversation_context(self, user_id: str):
        return self.conversation_manager.get_conversation_context(user_id)

    def get_queue_status(self):
        return self.conversation_manager.get_queue_status()

    def clear_pending_queue(self):
        return self.conversation_manager.clear_pending_queue()

    def get_debug_info(self):
        return self.message_processor.get_debug_info() 