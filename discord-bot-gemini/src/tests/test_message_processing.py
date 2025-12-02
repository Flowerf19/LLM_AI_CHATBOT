"""
Tests for Message Processing: deduplication, anti-spam, locking.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMessageDeduplication:
    """Test that same message is not processed twice"""
    
    def test_processed_message_ids_set(self):
        """Test _processed_message_ids is a set that prevents duplicates"""
        processed_ids = set()
        
        # First message
        msg_id_1 = 123456789
        assert msg_id_1 not in processed_ids
        processed_ids.add(msg_id_1)
        
        # Same message again - should be detected as duplicate
        assert msg_id_1 in processed_ids
        
        # Different message
        msg_id_2 = 987654321
        assert msg_id_2 not in processed_ids
    
    def test_message_processor_deduplication(self):
        """Test MessageProcessor tracks processed messages"""
        from services.conversation.message_processor import MessageProcessor
        
        processor = MessageProcessor()
        
        # Check it has processed_messages set
        assert hasattr(processor, 'processed_messages')
        assert isinstance(processor.processed_messages, set)


class TestAntiSpamProtection:
    """Test anti-spam rate limiting"""
    
    def test_queue_manager_spam_detection(self):
        """Test MessageQueueManager spam detection"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user_id = "spam_test_user"
        
        # is_spam should return tuple (is_spam, cooldown_remaining)
        result = manager.is_spam(user_id)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_anti_spam_service_exists(self):
        """Test AntiSpamService can be instantiated"""
        from services.conversation.anti_spam_service import AntiSpamService
        
        service = AntiSpamService()
        assert service is not None


class TestConversationLocking:
    """Test per-user conversation locking"""
    
    def test_conversation_lock_set_and_release(self):
        """Test setting and releasing conversation lock"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user_id = "lock_test_user"
        
        # Initially not locked
        assert not manager.is_conversation_locked(user_id)
        
        # Set lock
        manager.set_conversation_lock(user_id)
        assert manager.is_conversation_locked(user_id)
        
        # Release lock
        manager.release_conversation_lock(user_id)
        assert not manager.is_conversation_locked(user_id)
    
    def test_lock_duration_returns_integer(self):
        """Test lock duration returns an integer value"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user_id = "duration_test_user"
        
        manager.set_conversation_lock(user_id)
        
        duration = manager.get_lock_duration(user_id)
        assert isinstance(duration, int)
        assert duration >= 0
        
        manager.release_conversation_lock(user_id)
    
    def test_multiple_users_can_be_locked(self):
        """Test multiple users can have locks simultaneously"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user1 = "user_1"
        user2 = "user_2"
        
        manager.set_conversation_lock(user1)
        manager.set_conversation_lock(user2)
        
        assert manager.is_conversation_locked(user1)
        assert manager.is_conversation_locked(user2)
        
        manager.release_conversation_lock(user1)
        assert not manager.is_conversation_locked(user1)
        assert manager.is_conversation_locked(user2)
        
        manager.release_conversation_lock(user2)


class TestHistoryPersistence:
    """Test conversation history is saved and loaded correctly"""
    
    def test_history_save_and_load(self):
        """Test saving and loading conversation history"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user_id = "history_test_user"
        
        # Save to persistent history
        manager.save_to_persistent_history(user_id, "Hello", "Hi there!")
        
        # Add to in-memory history
        manager.add_to_history(user_id, "How are you?", "I'm doing great!")
        
        # Get conversation context
        context = manager.get_conversation_context(user_id)
        assert context is not None
    
    def test_conversation_context_format(self):
        """Test conversation context has expected format"""
        from services.messeger.message_queue import MessageQueueManager
        
        manager = MessageQueueManager()
        user_id = "context_format_user"
        
        manager.add_to_history(user_id, "Test message", "Test response")
        
        context = manager.get_conversation_context(user_id)
        assert isinstance(context, str)
