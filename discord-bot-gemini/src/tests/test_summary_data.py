"""
Tests for SummaryDataManager - Repository layer for user summary data.
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch


class TestSummaryDataManager:
    """Test suite for SummaryDataManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create SummaryDataManager with temp directory."""
        with patch('services.user_summary.summary_data.os.path.dirname') as mock_dirname:
            # Mock path resolution to use temp dir
            mock_dirname.return_value = temp_dir
            from services.user_summary.summary_data import SummaryDataManager
            manager = SummaryDataManager()
            manager.summaries_dir = temp_dir
            return manager

    def test_get_user_history_no_file(self, data_manager):
        """Test get_user_history when file doesn't exist."""
        result = data_manager.get_user_history("nonexistent_user")
        assert result == []

    def test_get_user_history_with_data(self, data_manager, temp_dir):
        """Test get_user_history with existing data."""
        user_id = "test_user_123"
        history_data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Create history file
        history_file = os.path.join(temp_dir, f"{user_id}_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f)
        
        result = data_manager.get_user_history(user_id)
        assert result == history_data

    def test_get_user_history_invalid_json(self, data_manager, temp_dir):
        """Test get_user_history with invalid JSON."""
        user_id = "test_user_invalid"
        
        # Create invalid JSON file
        history_file = os.path.join(temp_dir, f"{user_id}_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write("not valid json {{{")
        
        result = data_manager.get_user_history(user_id)
        assert result == []

    def test_get_user_summary_no_file(self, data_manager):
        """Test get_user_summary when file doesn't exist."""
        result = data_manager.get_user_summary("nonexistent_user")
        assert result == ""

    def test_get_user_summary_with_data(self, data_manager, temp_dir):
        """Test get_user_summary with existing data."""
        user_id = "test_user_456"
        summary_data = {"name": "Test User", "interests": ["coding", "music"]}
        
        # Create summary file
        summary_file = os.path.join(temp_dir, f"{user_id}_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f)
        
        result = data_manager.get_user_summary(user_id)
        # Result should be JSON string
        assert "Test User" in result
        assert "coding" in result

    def test_save_user_summary_json_string(self, data_manager, temp_dir):
        """Test save_user_summary with JSON string."""
        user_id = "test_save_user"
        summary_data = {"name": "John", "age": 25}
        summary_str = json.dumps(summary_data)
        
        data_manager.save_user_summary(user_id, summary_str)
        
        # Verify file was created
        summary_file = os.path.join(temp_dir, f"{user_id}_summary.json")
        assert os.path.exists(summary_file)
        
        # Verify content
        with open(summary_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data["name"] == "John"
        assert saved_data["age"] == 25

    def test_save_user_summary_raw_text(self, data_manager, temp_dir):
        """Test save_user_summary with raw text (non-JSON)."""
        user_id = "test_raw_user"
        raw_text = "This is a raw text summary"
        
        data_manager.save_user_summary(user_id, raw_text)
        
        # Verify file was created with wrapped content
        summary_file = os.path.join(temp_dir, f"{user_id}_summary.json")
        assert os.path.exists(summary_file)

    def test_clear_user_summary(self, data_manager, temp_dir):
        """Test clear_user_summary removes files."""
        user_id = "test_clear_user"
        
        # Create summary files
        summary_file = os.path.join(temp_dir, f"{user_id}_summary.json")
        txt_file = os.path.join(temp_dir, f"{user_id}_summary.txt")
        
        with open(summary_file, 'w') as f:
            f.write('{"test": "data"}')
        with open(txt_file, 'w') as f:
            f.write("test data")
        
        # Clear
        data_manager.clear_user_summary(user_id)
        
        # Verify files removed
        assert not os.path.exists(summary_file)
        assert not os.path.exists(txt_file)
