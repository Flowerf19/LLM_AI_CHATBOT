"""
Tests for RelationshipDataManager - Repository layer for relationship data.
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch


class TestRelationshipDataManager:
    """Test suite for RelationshipDataManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create RelationshipDataManager with temp directory."""
        with patch('services.relationship.relationship_data.os.path.dirname') as mock_dirname:
            mock_dirname.return_value = temp_dir
            from services.relationship.relationship_data import RelationshipDataManager
            manager = RelationshipDataManager()
            manager.data_dir = temp_dir
            manager.relationships_file = os.path.join(temp_dir, 'relationships.json')
            manager.user_names_file = os.path.join(temp_dir, 'user_names.json')
            manager.interactions_file = os.path.join(temp_dir, 'interactions.json')
            manager.conversation_history_file = os.path.join(temp_dir, 'conversation_history.json')
            return manager

    def test_load_json_no_file(self, data_manager, temp_dir):
        """Test load_json when file doesn't exist."""
        result = data_manager.load_json(os.path.join(temp_dir, "nonexistent.json"))
        assert result == {}

    def test_load_json_with_data(self, data_manager, temp_dir):
        """Test load_json with existing data."""
        test_file = os.path.join(temp_dir, "test.json")
        test_data = {"key": "value", "number": 42}
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = data_manager.load_json(test_file)
        assert result == test_data

    def test_load_json_invalid_json(self, data_manager, temp_dir):
        """Test load_json with invalid JSON returns empty dict."""
        test_file = os.path.join(temp_dir, "invalid.json")
        
        with open(test_file, 'w') as f:
            f.write("not valid json {{{")
        
        result = data_manager.load_json(test_file)
        assert result == {}

    def test_save_json(self, data_manager, temp_dir):
        """Test save_json creates file with correct content."""
        test_file = os.path.join(temp_dir, "save_test.json")
        test_data = {"users": ["user1", "user2"], "count": 2}
        
        data_manager.save_json(test_file, test_data)
        
        assert os.path.exists(test_file)
        with open(test_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == test_data

    def test_load_relationships(self, data_manager, temp_dir):
        """Test load_relationships uses correct file."""
        rel_data = {"user1_user2": {"type": "friends"}}
        
        with open(data_manager.relationships_file, 'w', encoding='utf-8') as f:
            json.dump(rel_data, f)
        
        result = data_manager.load_relationships()
        assert result == rel_data

    def test_save_relationships(self, data_manager):
        """Test save_relationships writes to correct file."""
        rel_data = {"user1_user2": {"type": "colleagues"}}
        
        data_manager.save_relationships(rel_data)
        
        assert os.path.exists(data_manager.relationships_file)
        with open(data_manager.relationships_file, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        assert saved == rel_data

    def test_load_user_names(self, data_manager, temp_dir):
        """Test load_user_names uses correct file."""
        names_data = {"123": {"username": "TestUser", "real_name": "John"}}
        
        with open(data_manager.user_names_file, 'w', encoding='utf-8') as f:
            json.dump(names_data, f)
        
        result = data_manager.load_user_names()
        assert result == names_data

    def test_save_user_names(self, data_manager):
        """Test save_user_names writes to correct file."""
        names_data = {"456": {"username": "AnotherUser"}}
        
        data_manager.save_user_names(names_data)
        
        assert os.path.exists(data_manager.user_names_file)

    def test_load_interactions(self, data_manager, temp_dir):
        """Test load_interactions uses correct file."""
        interactions_data = {"user1_user2": {"interactions": [{"type": "mention"}]}}
        
        with open(data_manager.interactions_file, 'w', encoding='utf-8') as f:
            json.dump(interactions_data, f)
        
        result = data_manager.load_interactions()
        assert result == interactions_data

    def test_save_interactions(self, data_manager):
        """Test save_interactions writes to correct file."""
        interactions_data = {"user1_user3": {"interactions": []}}
        
        data_manager.save_interactions(interactions_data)
        
        assert os.path.exists(data_manager.interactions_file)

    def test_load_conversation_history(self, data_manager, temp_dir):
        """Test load_conversation_history uses correct file."""
        history_data = {"123_456": {"messages": [{"content": "hello"}]}}
        
        with open(data_manager.conversation_history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f)
        
        result = data_manager.load_conversation_history()
        assert result == history_data

    def test_save_conversation_history(self, data_manager):
        """Test save_conversation_history writes to correct file."""
        history_data = {"123_789": {"messages": []}}
        
        data_manager.save_conversation_history(history_data)
        
        assert os.path.exists(data_manager.conversation_history_file)
