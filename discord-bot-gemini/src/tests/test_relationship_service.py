"""
Tests for RelationshipService.
"""
from unittest.mock import Mock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestRelationshipServiceInitialization:
    """Test RelationshipService initialization"""
    
    def test_relationship_service_can_be_instantiated(self):
        """Test RelationshipService can be created with mock bot"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        assert service is not None
        assert service.data_manager is not None
    
    def test_relationship_service_loads_data(self):
        """Test RelationshipService loads existing data"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        assert isinstance(service.relationships, dict)
        assert isinstance(service.user_names, dict)


class TestUserNameManagement:
    """Test user name tracking"""
    
    def test_update_user_name_new_user(self):
        """Test updating name for new user"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        user_id = "test_user_12345"
        username = "TestUser"
        
        service.update_user_name(user_id, username)
        
        assert user_id in service.user_names
        assert service.user_names[user_id]['username'] == username
    
    def test_update_user_name_with_display_name(self):
        """Test updating with display name"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        user_id = "test_user_67890"
        service.update_user_name(user_id, "username", display_name="Display Name")
        
        assert service.user_names[user_id]['display_name'] == "Display Name"
    
    def test_update_user_name_with_real_name(self):
        """Test updating with real name"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        user_id = "test_user_real"
        service.update_user_name(user_id, "username", real_name="Nguyễn Văn A")
        
        assert service.user_names[user_id]['real_name'] == "Nguyễn Văn A"
    
    def test_get_user_display_name_fallback(self):
        """Test fallback display name for unknown user"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        name = service.get_user_display_name("unknown_user_1234")
        
        # Should return fallback format
        assert "1234" in name  # Last 4 digits of ID
    
    def test_get_user_display_name_priority(self):
        """Test display name priority: real > display > username"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        user_id = "priority_user"
        service.update_user_name(
            user_id, 
            "username", 
            display_name="DisplayName",
            real_name="Real Name"
        )
        
        # Should return real name (highest priority)
        name = service.get_user_display_name(user_id)
        assert name == "Real Name"


class TestMessageProcessing:
    """Test message processing"""
    
    def test_process_message_updates_user_name(self):
        """Test process_message updates user name"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        author_id = "msg_author_123"
        author_username = "MessageAuthor"
        
        service.process_message(author_id, author_username, "Hello world!")
        
        assert author_id in service.user_names
    
    def test_process_message_records_conversation(self):
        """Test process_message records conversation history"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        # Process a message
        service.process_message("user_conv", "ConvUser", "Test message content")
        
        # Conversation history should exist
        assert isinstance(service.conversation_history, dict)


class TestRelationshipDataManager:
    """Test RelationshipDataManager separately"""
    
    def test_data_manager_load_relationships(self):
        """Test loading relationships"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        data = manager.load_relationships()
        
        assert isinstance(data, dict)
    
    def test_data_manager_load_user_names(self):
        """Test loading user names"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        data = manager.load_user_names()
        
        assert isinstance(data, dict)
    
    def test_data_manager_load_interactions(self):
        """Test loading interactions"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        data = manager.load_interactions()
        
        assert isinstance(data, dict)


class TestUserSummary:
    """Test user summary methods"""
    
    def test_get_all_users_summary(self):
        """Test getting summary of all users"""
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        service = RelationshipService(mock_bot)
        
        # Add a test user first
        service.update_user_name("summary_user", "SummaryUser")
        
        summary = service.get_all_users_summary()
        
        assert 'total_users' in summary
        assert 'total_relationships' in summary
        assert 'users' in summary
        assert isinstance(summary['users'], list)
