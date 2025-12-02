"""
Tests for Queue Commands module.

Tests the queue_commands.py functionality including:
- queue_status command
- clear_queue command  
- debug_duplicate command
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


class TestQueueCommands:
    """Test suite for QueueCommands Cog."""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot instance."""
        bot = MagicMock()
        bot.get_cog = MagicMock(return_value=None)
        return bot
    
    @pytest.fixture
    def mock_ctx(self):
        """Create a mock context."""
        ctx = MagicMock()
        ctx.reply = AsyncMock()
        ctx.author = MagicMock()
        ctx.author.guild_permissions = MagicMock()
        ctx.author.guild_permissions.manage_messages = True
        return ctx
    
    @pytest.fixture
    def mock_queue_manager(self):
        """Create a mock queue manager."""
        queue_manager = MagicMock()
        queue_manager.get_queue_status = MagicMock(return_value={
            'currently_responding_to': None,
            'lock_duration': 0,
            'pending_count': 0,
            'pending_users': []
        })
        queue_manager.clear_pending_queue = MagicMock(return_value=5)
        queue_manager.message_processor = MagicMock()
        queue_manager.message_processor.get_debug_info = MagicMock(return_value={
            'processed_count': 10,
            'processing_count': 1,
            'locks_count': 2,
            'recent_processed': ['msg1', 'msg2'],
            'current_processing': ['msg3'],
            'locked_messages': ['msg4']
        })
        return queue_manager
    
    @pytest.fixture
    def queue_commands(self, mock_bot):
        """Create QueueCommands instance with mock bot."""
        from services.commands.queue_commands import QueueCommands
        return QueueCommands(mock_bot)

    @pytest.mark.asyncio
    async def test_queue_status_no_manager(self, queue_commands, mock_ctx):
        """Test queue_status when queue manager is not available."""
        # Call the callback directly (bypass Command wrapper)
        await queue_commands.queue_status_command.callback(queue_commands, mock_ctx)
        mock_ctx.reply.assert_called_once()
        call_args = mock_ctx.reply.call_args[0][0]
        assert "not available" in call_args

    @pytest.mark.asyncio
    async def test_queue_status_with_manager(self, queue_commands, mock_ctx, mock_queue_manager, mock_bot):
        """Test queue_status with available queue manager."""
        # Setup LLMMessageService mock with queue_manager
        llm_service = MagicMock()
        llm_service.queue_manager = mock_queue_manager
        mock_bot.get_cog = MagicMock(return_value=llm_service)
        
        await queue_commands.queue_status_command.callback(queue_commands, mock_ctx)
        
        mock_ctx.reply.assert_called_once()
        # Check that an embed was sent
        call_kwargs = mock_ctx.reply.call_args[1]
        assert 'embed' in call_kwargs

    @pytest.mark.asyncio
    async def test_clear_queue_no_permission(self, queue_commands, mock_ctx, mock_queue_manager, mock_bot):
        """Test clear_queue without manage_messages permission."""
        mock_ctx.author.guild_permissions.manage_messages = False
        llm_service = MagicMock()
        llm_service.queue_manager = mock_queue_manager
        mock_bot.get_cog = MagicMock(return_value=llm_service)
        
        await queue_commands.clear_queue_command.callback(queue_commands, mock_ctx)
        
        mock_ctx.reply.assert_called_once()
        call_args = mock_ctx.reply.call_args[0][0]
        assert "permission" in call_args.lower()

    @pytest.mark.asyncio
    async def test_clear_queue_with_permission(self, queue_commands, mock_ctx, mock_queue_manager, mock_bot):
        """Test clear_queue with proper permissions."""
        mock_ctx.author.guild_permissions.manage_messages = True
        llm_service = MagicMock()
        llm_service.queue_manager = mock_queue_manager
        mock_bot.get_cog = MagicMock(return_value=llm_service)
        
        await queue_commands.clear_queue_command.callback(queue_commands, mock_ctx)
        
        mock_queue_manager.clear_pending_queue.assert_called_once()
        mock_ctx.reply.assert_called_once()
        call_args = mock_ctx.reply.call_args[0][0]
        assert "5" in call_args  # 5 messages cleared

    @pytest.mark.asyncio
    async def test_debug_duplicate_command(self, queue_commands, mock_ctx, mock_queue_manager, mock_bot):
        """Test debug_duplicate command returns debug info."""
        llm_service = MagicMock()
        llm_service.queue_manager = mock_queue_manager
        mock_bot.get_cog = MagicMock(return_value=llm_service)
        
        await queue_commands.debug_duplicate_command.callback(queue_commands, mock_ctx)
        
        mock_queue_manager.message_processor.get_debug_info.assert_called_once()
        mock_ctx.reply.assert_called_once()
