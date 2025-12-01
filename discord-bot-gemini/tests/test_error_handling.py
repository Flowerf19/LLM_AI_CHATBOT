import asyncio
import os
import json
from unittest.mock import MagicMock, AsyncMock
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from services.user_summary.summary_service import SummaryService

async def _run_error_handling_test():
    mock_llm = MagicMock()
    mock_llm.generate_response = AsyncMock(side_effect=Exception('LLM failure'))

    service = SummaryService(mock_llm)
    test_user_id = 'test_err_123'

    # create history file
    history_file = service.summaries_dir / f"{test_user_id}_history.json"
    if history_file.exists():
        history_file.unlink()
    history = [
        {"role": "user", "content": "Tôi tên là X"},
        {"role": "user", "content": "Tôi thích chơi game"}
    ]
    os.makedirs(service.summaries_dir, exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False)

    # call update
    res = await service.update_summary_smart(test_user_id, 'Tôi tên là X')
    return res


def test_error_handling():
    res = asyncio.run(_run_error_handling_test())
    # We expect None or empty result due to LLM failure
    assert res is None or res == ''
