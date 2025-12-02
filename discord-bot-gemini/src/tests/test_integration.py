"""
Integration tests for end-to-end message flow.
Tests the interaction between services without actual Discord/API calls.
"""
import pytest
import tempfile
import json
from unittest.mock import Mock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSummaryServiceIntegration:
    """Test SummaryService with real DataManager and Parser"""
    
    def setup_method(self):
        """Setup test environment with temp directory"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup temp files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_summary_service_initialization(self):
        """Test SummaryService can be initialized"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        assert service is not None
        assert service.data_manager is not None
        assert service.parser is not None
    
    def test_summary_service_get_nonexistent_user(self):
        """Test getting summary for user that doesn't exist"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        summary = service.get_user_summary("nonexistent_user_999")
        assert summary == ""
    
    def test_summary_service_should_update_no_summary(self):
        """Test should_update_summary returns True for new user"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        result = service.should_update_summary("new_user_123")
        assert result
    
    def test_summary_service_increment_message_count(self):
        """Test message count incrementing"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_user_456"
        
        assert service._message_count_since_update.get(user_id, 0) == 0
        
        service.increment_message_count(user_id)
        assert service._message_count_since_update[user_id] == 1
        
        service.increment_message_count(user_id)
        assert service._message_count_since_update[user_id] == 2
    
    def test_summary_service_reset_tracking(self):
        """Test reset_update_tracking clears counters"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_user_789"
        
        service._message_count_since_update[user_id] = 10
        service._last_update_time[user_id] = 0
        
        service.reset_update_tracking(user_id)
        
        assert service._message_count_since_update[user_id] == 0
        assert service._last_update_time[user_id] > 0


class TestSummaryParserIntegration:
    """Test SummaryParser with real data transformations"""
    
    def test_full_parse_and_format_cycle(self):
        """Test parsing text and formatting back to JSON"""
        from services.user_summary.summary_parser import SummaryParser
        
        parser = SummaryParser()
        ai_response = "Tên: Nguyễn Văn A\nTuổi: 25\nSinh nhật: 15/03/1999\nCông nghệ: Python, JavaScript"
        
        fields = parser.parse_to_dict(ai_response)
        assert fields["Tên"] == "Nguyễn Văn A"
        assert fields["Tuổi"] == "25"
        
        json_str = parser.format_to_json(fields)
        assert json_str is not None
        
        data = json.loads(json_str)
        assert data["basic_info"]["name"] == "Nguyễn Văn A"
        assert data["basic_info"]["age"] == "25"
    
    def test_merge_preserves_existing_data(self):
        """Test merging new data with existing summary"""
        from services.user_summary.summary_parser import SummaryParser
        
        parser = SummaryParser()
        
        old_summary = json.dumps({
            "basic_info": {"name": "Người dùng cũ", "age": "30", "birthday": "Không có"},
            "hobbies_and_passion": {"tech": "Java", "entertainment": "Không có", "other": "Không có"}
        }, ensure_ascii=False)
        
        new_response = "Tên: Người dùng mới\nTuổi: Không có\nGiải trí: Chơi game"
        
        merged = parser.merge_fields(old_summary, new_response)
        data = json.loads(merged)
        
        assert data["basic_info"]["name"] == "Người dùng mới"
        assert data["basic_info"]["age"] == "30"
        assert data["hobbies_and_passion"]["entertainment"] == "Chơi game"
        assert data["hobbies_and_passion"]["tech"] == "Java"


class TestRelationshipServiceIntegration:
    """Test RelationshipService with real DataManager"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_relationship_data_manager_initialization(self):
        """Test RelationshipDataManager can be initialized"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        assert manager is not None
    
    def test_relationship_data_manager_save_and_load(self):
        """Test saving and loading relationships"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        loaded = manager.load_relationships()
        assert isinstance(loaded, dict)


class TestContextBuilderIntegration:
    """Test ContextBuilder context assembly"""
    
    def test_context_builder_builds_context(self):
        """Test ContextBuilder can build enhanced context"""
        from services.messeger.context_builder import ContextBuilder
        from services.user_summary.summary_service import SummaryService
        from services.relationship.relationship_service import RelationshipService
        
        mock_bot = Mock()
        mock_bot.user = Mock()
        mock_bot.user.id = 12345
        mock_bot.get_cog = Mock(return_value=None)
        
        summary_service = SummaryService()
        relationship_service = RelationshipService(mock_bot)
        context_builder = ContextBuilder(mock_bot, summary_service, relationship_service)
        
        context = context_builder.build_enhanced_context(
            "test_user", 
            '{"Tên": "Test User"}', 
            [], 
            "User: Hello\nBot: Hi!"
        )
        
        assert context is not None
        assert len(context) > 0


class TestMessageFlowEndToEnd:
    """End-to-end test simulating full message flow"""
    
    @pytest.mark.asyncio
    async def test_full_message_flow_mock(self):
        """Test the complete message flow with mocked external services"""
        from services.user_summary.summary_service import SummaryService
        from services.user_summary.summary_parser import SummaryParser
        
        summary_service = SummaryService()
        parser = SummaryParser()
        user_id = "e2e_test_user"
        
        # 1. User sends message
        summary_service.increment_message_count(user_id)
        assert summary_service._message_count_since_update[user_id] == 1
        
        # 2. Check if should update
        assert summary_service.should_update_summary(user_id)
        
        # 3. Simulate AI response
        ai_response = "Tên: E2E Test User\nTuổi: 25\nCông nghệ: Python"
        
        # 4. Parse and format
        fields = parser.parse_to_dict(ai_response)
        summary_json = parser.format_to_json(fields)
        
        # 5. Verify result
        data = json.loads(summary_json)
        assert data["basic_info"]["name"] == "E2E Test User"
        assert data["basic_info"]["age"] == "25"
        
        # 6. Reset tracking
        summary_service.reset_update_tracking(user_id)
        assert summary_service._message_count_since_update[user_id] == 0
