import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import services.ai.gemini_service as gs
# Patch GeminiService before importing modules that use it
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

async def _run_concurrency_test(count=50):
    mock_bot = MagicMock()
    mock_bot.user = MagicMock()
    mock_bot.user.id = 999
    mock_bot.process_commands = AsyncMock()

    # Patch GeminiService
    gs.GeminiService = MagicMock()
    gs.GeminiService.return_value.generate_response = AsyncMock(return_value='{"basic_info": {"name": "Test"}}')

    service = LLMMessageService(mock_bot)

    handle_count = {'count': 0}
    async def fake_handle(message):
        await asyncio.sleep(0)
        handle_count['count'] += 1

    service._handle_message = fake_handle
    service.queue_manager.message_processor.should_process_message = AsyncMock(return_value=True)

    # Create tasks
    tasks = []
    for i in range(count):
        msg = DummyMessage(id=1000 + i)
        tasks.append(service.on_message(msg))

    await asyncio.gather(*tasks)
    return handle_count['count']


def test_concurrency():
    result = asyncio.run(_run_concurrency_test(60))
    assert result == 60, f"Expected 60 processed messages, got {result}"
