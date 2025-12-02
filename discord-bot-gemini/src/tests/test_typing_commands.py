"""
Tests for Typing Commands module.

Tests the typing_commands.py functionality including:
- test_typing command
- typing_settings command
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestTypingCommands:
    """Test suite for TypingCommands Cog."""
    
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
        ctx.message = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 12345
        ctx.author.guild_permissions = MagicMock()
        ctx.author.guild_permissions.manage_messages = True
        return ctx
    
    @pytest.fixture
    def typing_commands(self, mock_bot):
        """Create TypingCommands instance with mock bot."""
        from services.commands.typing_commands import TypingCommands
        return TypingCommands(mock_bot)

    @pytest.mark.asyncio
    async def test_test_typing_no_llm_service(self, typing_commands, mock_ctx):
        """Test test_typing command when LLMMessageService is not available."""
        # Call the callback directly (bypass Command wrapper)
        await typing_commands.test_typing_command.callback(typing_commands, mock_ctx)
        
        # Should fallback to simple reply
        mock_ctx.reply.assert_called_once()
        call_args = mock_ctx.reply.call_args[0][0]
        assert "typing effect" in call_args.lower()

    @pytest.mark.asyncio
    async def test_test_typing_with_llm_service(self, typing_commands, mock_ctx, mock_bot):
        """Test test_typing command with LLMMessageService available."""
        llm_service = MagicMock()
        llm_service.send_response_in_parts = AsyncMock()
        mock_bot.get_cog = MagicMock(return_value=llm_service)
        
        await typing_commands.test_typing_command.callback(typing_commands, mock_ctx)
        
        llm_service.send_response_in_parts.assert_called_once()

    @pytest.mark.asyncio
    async def test_typing_settings_command(self, typing_commands, mock_ctx):
        """Test typing_settings command returns settings embed."""
        with patch('services.commands.typing_commands.Config') as mock_config:
            mock_config.ENABLE_TYPING_SIMULATION = True
            mock_config.TYPING_SPEED_WPM = 250
            mock_config.MIN_TYPING_DELAY = 0.5
            mock_config.MAX_TYPING_DELAY = 8.0
            mock_config.PART_BREAK_DELAY = 0.6
            
            await typing_commands.typing_settings_command.callback(typing_commands, mock_ctx)
            
            mock_ctx.reply.assert_called_once()
            # Check that an embed was sent
            call_kwargs = mock_ctx.reply.call_args[1]
            assert 'embed' in call_kwargs

    @pytest.mark.asyncio
    async def test_typing_settings_disabled(self, typing_commands, mock_ctx):
        """Test typing_settings shows disabled status."""
        with patch('services.commands.typing_commands.Config') as mock_config:
            mock_config.ENABLE_TYPING_SIMULATION = False
            mock_config.TYPING_SPEED_WPM = 250
            mock_config.MIN_TYPING_DELAY = 0.5
            mock_config.MAX_TYPING_DELAY = 8.0
            mock_config.PART_BREAK_DELAY = 0.6
            
            await typing_commands.typing_settings_command.callback(typing_commands, mock_ctx)
            
            mock_ctx.reply.assert_called_once()
