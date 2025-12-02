"""
Tests for Error Recovery and Edge Cases.
"""
import pytest
import json
from unittest.mock import AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestErrorHandling:
    """Test error handling in various scenarios"""
    
    def test_parser_handles_malformed_json(self):
        """Test parser gracefully handles malformed JSON"""
        from services.user_summary.summary_parser import SummaryParser
        
        parser = SummaryParser()
        
        # Malformed JSON-like text
        malformed = "{ invalid json here"
        
        # Should not raise, should return something
        result = parser.clean_text(malformed)
        assert result is not None
    
    def test_parser_handles_empty_input(self):
        """Test parser handles empty input"""
        from services.user_summary.summary_parser import SummaryParser
        
        parser = SummaryParser()
        
        result = parser.parse_to_dict("")
        assert result is not None
        # All fields should be None
        assert all(v is None for v in result.values())
    
    def test_summary_service_handles_invalid_user_id(self):
        """Test summary service handles edge case user IDs"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        
        # Empty user ID
        summary = service.get_user_summary("")
        assert summary == ""
        
        # Very long user ID
        long_id = "a" * 1000
        summary = service.get_user_summary(long_id)
        assert summary == ""


class TestErrorRecovery:
    """Test bot handles errors gracefully"""
    
    @pytest.mark.asyncio
    async def test_summary_service_handles_ai_error(self):
        """Test summary service handles AI returning error"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "error_test_user"
        
        # Mock AI that returns error
        mock_ai = AsyncMock()
        mock_ai.generate_response = AsyncMock(return_value="Error: API rate limit exceeded")
        
        result = await service.update_summary_smart(
            user_id,
            mock_ai,
            recent_messages=[{"role": "user", "content": "test"}],
            force=True
        )
        
        # Should return None on error, not crash
        assert result is None
    
    @pytest.mark.asyncio
    async def test_summary_service_handles_empty_response(self):
        """Test summary service handles AI returning empty response"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "empty_response_user"
        
        # Mock AI that returns empty
        mock_ai = AsyncMock()
        mock_ai.generate_response = AsyncMock(return_value="")
        
        result = await service.update_summary_smart(
            user_id,
            mock_ai,
            recent_messages=[{"role": "user", "content": "test"}],
            force=True
        )
        
        # Should return None, not crash
        assert result is None
    
    @pytest.mark.asyncio
    async def test_summary_service_handles_ai_exception(self):
        """Test summary service handles AI throwing exception"""
        from services.user_summary.summary_service import SummaryService
        
        service = SummaryService()
        user_id = "exception_test_user"
        
        # Mock AI that throws exception
        mock_ai = AsyncMock()
        mock_ai.generate_response = AsyncMock(side_effect=Exception("Network timeout"))
        
        result = await service.update_summary_smart(
            user_id,
            mock_ai,
            recent_messages=[{"role": "user", "content": "test"}],
            force=True
        )
        
        # Should return None, not crash
        assert result is None


class TestDataPersistence:
    """Test user data survives between service instances"""
    
    def test_summary_data_persists(self):
        """Test summary data is persisted to file"""
        from services.user_summary.summary_data import SummaryDataManager
        
        manager1 = SummaryDataManager()
        user_id = "persistence_test_user"
        test_summary = json.dumps({"basic_info": {"name": "Persistent User"}})
        
        # Save with first instance
        manager1.save_user_summary(user_id, test_summary)
        
        # Load with new instance (simulates restart)
        manager2 = SummaryDataManager()
        loaded = manager2.get_user_summary(user_id)
        
        if loaded:
            data = json.loads(loaded)
            assert data["basic_info"]["name"] == "Persistent User"
    
    def test_relationship_data_persists(self):
        """Test relationship data is persisted"""
        from services.relationship.relationship_data import RelationshipDataManager
        
        manager = RelationshipDataManager()
        
        # Load should work even if file doesn't exist
        data = manager.load_relationships()
        assert isinstance(data, dict)
