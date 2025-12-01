import asyncio
import os
import json
import logging
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

# Setup paths
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from services.user_summary.summary_service import SummaryService
from config.settings import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _run_summary_update():
    print("=== STARTING SUMMARY UPDATE TEST ===")
    
    # 1. Setup Mock LLM Service
    mock_llm = MagicMock()
    # Mock response simulating LLM extracting info
    # Case 1: LLM returns JSON
    mock_llm.generate_response = AsyncMock(return_value=json.dumps({
        "basic_info": {
            "name": "Hòa",
            "age": "25",
            "birthday": "01/01/2000"
        },
        "hobbies_and_passion": {
            "tech": "AI, Coding",
            "entertainment": "Game",
            "other": "Ngủ"
        }
    }))
    
    # 2. Initialize SummaryService
    # We use a test user ID to avoid overwriting real data
    test_user_id = "test_user_12345"
    service = SummaryService(mock_llm)
    
    # Ensure clean state
    summary_file = service.summaries_dir / f"{test_user_id}_summary.json"
    history_file = service.summaries_dir / f"{test_user_id}_history.json"
    
    if summary_file.exists():
        os.remove(summary_file)
    if history_file.exists():
        os.remove(history_file)
        
    # Create dummy history
    history_data = [
        {"role": "user", "content": "Chào, mình tên là Hòa, năm nay 25 tuổi."},
        {"role": "model", "content": "Chào Hòa nhé."},
        {"role": "user", "content": "Mình thích code AI và chơi game."}
    ]
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False)
        
    print(f"Created dummy history for {test_user_id}")

    # 3. Trigger Update
    # We force update by passing a message with a keyword or just relying on the logic
    # The logic checks for keywords or template status.
    # Since file is missing, it might return empty string, which is treated as template?
    # Let's check get_user_summary
    
    current_summary = service.get_user_summary(test_user_id)
    print(f"Current Summary (Before): '{current_summary}'")
    
    print("Triggering update_summary_smart...")
    # We pass a message containing a keyword to force update
    updated_summary = await service.update_summary_smart(test_user_id, "Mình tên là Hòa")
    
    print(f"Updated Summary Result: {updated_summary[:100]}...")
    
    # 4. Verify File Content
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        print("\n=== VERIFICATION ===")
        print(f"File exists: {summary_file}")
        print("Content:")
        print(json.dumps(saved_data, indent=2, ensure_ascii=False))
        
        # Assertions
        basic_info = saved_data.get("basic_info", {})
        if basic_info.get("name") == "Hòa" and basic_info.get("age") == "25":
            print("\n✅ TEST PASSED: Name and Age updated correctly.")
        else:
            print("\n❌ TEST FAILED: Data mismatch.")
    else:
        print("\n❌ TEST FAILED: Summary file not created.")

    # Cleanup
    # if summary_file.exists(): os.remove(summary_file)
    # if history_file.exists(): os.remove(history_file)

def test_summary_update():
    # Wrapper for pytest to run the async test synchronously
    asyncio.run(_run_summary_update())
