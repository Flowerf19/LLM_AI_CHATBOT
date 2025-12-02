"""
Tests for Summary Generation Flow.
Tests bot creates summary when chatting with user.
"""
import pytest
import json
from unittest.mock import AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSummaryGenerationFlow:
    """
    Test bot creates summary when chatting with user.
    Simulates the full flow: message -> threshold check -> AI call -> save summary
    """
    
    @pytest.mark.asyncio
    async def test_summary_created_when_threshold_reached(self):
        """Test summary is created when message threshold is reached"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_summary_threshold_user"
        
        # Simulate reaching MESSAGE_THRESHOLD (8 messages)
        for _ in range(8):
            service.increment_message_count(user_id)
        
        # Should need update now
        should_update = service.should_update_summary(user_id)
        assert should_update, "Should update after MESSAGE_THRESHOLD messages"
    
    @pytest.mark.asyncio
    async def test_update_summary_smart_with_mocked_ai(self):
        """Test update_summary_smart calls AI and saves result"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_ai_summary_user"
        
        # Create mock AI service
        mock_ai = AsyncMock()
        mock_ai.generate_response = AsyncMock(return_value="Tên: AI Test User\nTuổi: 30\nCông nghệ: Python, FastAPI")
        
        # Prepare some history
        test_history = [
            {"role": "user", "content": "Xin chào, tôi là Test User"},
            {"role": "assistant", "content": "Chào bạn!"},
            {"role": "user", "content": "Tôi thích Python lắm"},
            {"role": "assistant", "content": "Python rất tuyệt!"},
        ]
        
        # Force update
        result = await service.update_summary_smart(
            user_id,
            mock_ai,
            recent_messages=test_history,
            force=True
        )
        
        # Verify AI was called
        assert mock_ai.generate_response.called
        
        # Verify result is valid JSON
        if result:
            data = json.loads(result)
            assert "basic_info" in data
            assert data["basic_info"]["name"] == "AI Test User"
    
    @pytest.mark.asyncio
    async def test_summary_not_updated_below_threshold(self):
        """Test summary is NOT updated when below threshold"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_below_threshold_user"
        
        # Set an existing summary via save method
        existing_summary = json.dumps({
            "basic_info": {"name": "Existing User", "age": "25", "birthday": "Không có"},
            "hobbies_and_passion": {"tech": "Không có", "entertainment": "Không có", "other": "Không có"},
            "personality_and_style": {"communication_style": "Không có", "behavior_patterns": "Không có", "topics_interests": "Không có"},
            "relationship_notes": {"user_relationship": "Không có", "mentioned_relationships": "Không có", "key_interactions": "Không có"}
        }, ensure_ascii=False)
        
        service.data_manager.save_user_summary(user_id, existing_summary)
        
        # Only 2 messages - below threshold
        service.increment_message_count(user_id)
        service.increment_message_count(user_id)
        
        # Should NOT need update
        should_update = service.should_update_summary(user_id)
        assert not should_update, "Should NOT update when below threshold"
    
    @pytest.mark.asyncio
    async def test_template_summary_updates_faster(self):
        """Test template summaries update with lower threshold (3 messages)"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_template_user"
        
        # Create a template summary (has "[Không có]" placeholder values)
        template_summary = json.dumps({
            "basic_info": {"name": "[Không có]", "age": "[Không có]", "birthday": "[Không có]"},
            "hobbies_and_passion": {"tech": "[Không có]", "entertainment": "[Không có]", "other": "[Không có]"},
            "personality_and_style": {"communication_style": "[Không có]", "behavior_patterns": "[Không có]", "topics_interests": "[Không có]"},
            "relationship_notes": {"user_relationship": "[Không có]", "mentioned_relationships": "[Không có]", "key_interactions": "[Không có]"}
        }, ensure_ascii=False)
        
        service.data_manager.save_user_summary(user_id, template_summary)
        
        # Only 3 messages - at TEMPLATE_MESSAGE_THRESHOLD
        for _ in range(3):
            service.increment_message_count(user_id)
        
        should_update = service.should_update_summary(user_id)
        assert should_update, "Template summary should update at TEMPLATE_MESSAGE_THRESHOLD (3)"
    
    @pytest.mark.asyncio
    async def test_summary_merge_preserves_known_data(self):
        """Test merging new summary preserves existing known information"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "test_merge_user"
        
        # Set existing summary with some known data
        existing = json.dumps({
            "basic_info": {"name": "Nguyễn A", "age": "25", "birthday": "15/03"},
            "hobbies_and_passion": {"tech": "Python", "entertainment": "Không có", "other": "Không có"},
            "personality_and_style": {"communication_style": "Thân thiện", "behavior_patterns": "Không có", "topics_interests": "Không có"},
            "relationship_notes": {"user_relationship": "Không có", "mentioned_relationships": "Không có", "key_interactions": "Không có"}
        }, ensure_ascii=False)
        
        # Mock AI returns partial info (some fields as "Không có")
        mock_ai = AsyncMock()
        mock_ai.generate_response = AsyncMock(return_value="Tên: Không có\nTuổi: Không có\nGiải trí: Chơi game, Đọc manga")
        
        # Save existing and force update
        service.data_manager.save_user_summary(user_id, existing)
        
        result = await service.update_summary_smart(
            user_id, 
            mock_ai, 
            recent_messages=[{"role": "user", "content": "test"}],
            force=True
        )
        
        if result:
            data = json.loads(result)
            # Should preserve existing name (AI said "Không có")
            assert data["basic_info"]["name"] == "Nguyễn A"
            # Should preserve existing age 
            assert data["basic_info"]["age"] == "25"
            # Should add new entertainment info
            assert "Chơi game" in data["hobbies_and_passion"]["entertainment"]
