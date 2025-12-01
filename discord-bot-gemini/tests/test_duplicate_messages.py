import asyncio
from unittest.mock import MagicMock, AsyncMock
import os
import sys

# Setup path to src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import services.ai.gemini_service as gs
# Patch GeminiService early to avoid loading prompts or contacting LLM when modules import
gs.GeminiService = MagicMock()
gs.GeminiService.return_value.generate_response = AsyncMock(return_value='{"basic_info": {"name": "Test"}}')
from services.messeger.llm_message_service import LLMMessageService

class DummyAuthor:
    def __init__(self, id=111):
        self.id = id

class DummyChannel:
    def __init__(self, id=222):
        self.id = id

class DummyMessage:
    def __init__(self, id=1, author=None, content='hello', channel=None):
        self.id = id
        self.author = author or DummyAuthor()
        self.content = content
        self.channel = channel or DummyChannel()

async def _run_duplicate_message_processing():
    mock_bot = MagicMock()
    # Create unique bot user id so message.author != bot.user
    mock_bot.user = MagicMock()
    mock_bot.user.id = 999
    mock_bot.process_commands = AsyncMock()

    # Patch GeminiService to avoid loading prompts or contacting LLM
    gs.GeminiService = MagicMock()
    gs.GeminiService.return_value.generate_response = AsyncMock(return_value='{"basic_info": {"name": "Test"}}')
    # Instantiate service
    service = LLMMessageService(mock_bot)

    # Replace queue processor with custom stub that counts invocations
    call_count = {'count': 0}

    async def fake_process_with_lock(message, func):
        call_count['count'] += 1
        # simulate handling
        await asyncio.sleep(0)  # allow concurrency
        return await func(message)

    # Force should_process_message to always return True
    service.queue_manager.message_processor.should_process_message = AsyncMock(return_value=True)
    service.queue_manager.message_processor.process_with_lock = fake_process_with_lock

    # Replace _handle_message to avoid heavy processing and just return
    async def fake_handle(message):
        await asyncio.sleep(0)
        return

    service._handle_message = fake_handle

    # Create two messages with the same id -> simulate duplicate
    message1 = DummyMessage(id=1000)
    message2 = DummyMessage(id=1000)

    # Call on_message concurrently
    await asyncio.gather(service.on_message(message1), service.on_message(message2))

    assert call_count['count'] == 1, f"Duplicate message processed {call_count['count']} times"

def test_duplicate_message_processing():
    asyncio.run(_run_duplicate_message_processing())
