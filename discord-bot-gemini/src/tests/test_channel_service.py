"""
Tests for ChannelService.
"""
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestChannelServiceInitialization:
    """Test ChannelService initialization"""
    
    def test_channel_service_can_be_instantiated(self):
        """Test ChannelService can be created"""
        from services.channel.channel_service import ChannelService
        
        service = ChannelService()
        assert service is not None
    
    def test_channel_service_has_api_url(self):
        """Test ChannelService has API URL configured"""
        from services.channel.channel_service import ChannelService
        
        service = ChannelService()
        assert hasattr(service, 'gemini_api_url')


class TestChannelServiceMethods:
    """Test ChannelService CRUD methods"""
    
    @patch('services.channel.channel_service.requests.get')
    def test_get_channel_info_success(self, mock_get):
        """Test get_channel_info returns data on success"""
        from services.channel.channel_service import ChannelService
        
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "test-channel"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ChannelService()
        result = service.get_channel_info("123")
        
        assert result is not None
        assert result["id"] == "123"
    
    @patch('services.channel.channel_service.requests.get')
    def test_get_channel_info_failure(self, mock_get):
        """Test get_channel_info returns None on failure"""
        from services.channel.channel_service import ChannelService
        import requests
        
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        service = ChannelService()
        result = service.get_channel_info("123")
        
        assert result is None
    
    @patch('services.channel.channel_service.requests.post')
    def test_create_channel_success(self, mock_post):
        """Test create_channel returns data on success"""
        from services.channel.channel_service import ChannelService
        
        mock_response = Mock()
        mock_response.json.return_value = {"id": "456", "name": "new-channel"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        service = ChannelService()
        result = service.create_channel({"name": "new-channel"})
        
        assert result is not None
        assert result["name"] == "new-channel"
    
    @patch('services.channel.channel_service.requests.post')
    def test_create_channel_failure(self, mock_post):
        """Test create_channel returns None on failure"""
        from services.channel.channel_service import ChannelService
        import requests
        
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        service = ChannelService()
        result = service.create_channel({"name": "new-channel"})
        
        assert result is None
    
    @patch('services.channel.channel_service.requests.put')
    def test_update_channel_success(self, mock_put):
        """Test update_channel returns data on success"""
        from services.channel.channel_service import ChannelService
        
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "updated-channel"}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response
        
        service = ChannelService()
        result = service.update_channel("123", {"name": "updated-channel"})
        
        assert result is not None
    
    @patch('services.channel.channel_service.requests.delete')
    def test_delete_channel_success(self, mock_delete):
        """Test delete_channel returns data on success"""
        from services.channel.channel_service import ChannelService
        
        mock_response = Mock()
        mock_response.json.return_value = {"deleted": True}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response
        
        service = ChannelService()
        result = service.delete_channel("123")
        
        assert result is not None
    
    @patch('services.channel.channel_service.requests.delete')
    def test_delete_channel_failure(self, mock_delete):
        """Test delete_channel returns None on failure"""
        from services.channel.channel_service import ChannelService
        import requests
        
        mock_delete.side_effect = requests.exceptions.RequestException("Connection error")
        
        service = ChannelService()
        result = service.delete_channel("123")
        
        assert result is None
