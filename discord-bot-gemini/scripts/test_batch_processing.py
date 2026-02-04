"""
Test script để chạy thử batch processing với data thật từ recent_log.json
Run: python scripts/test_batch_processing.py
"""
import sys
import os
import asyncio
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.conversation.batch_processor import batch_processor
from src.services.conversation.recent_log_service import recent_log_service
from src.utils.helpers import get_logger

logger = get_logger(__name__)

async def test_batch_processing():
    """Test batch processing với data hiện tại"""
    
    print("=" * 60)
    print("🧪 TEST BATCH PROCESSING")
    print("=" * 60)
    
    # 1. Kiểm tra recent_log có data không
    try:
        log_file = project_root / "data" / "recent_log.json"
        if not log_file.exists():
            print("❌ recent_log.json không tồn tại!")
            return
            
        print(f"✅ Found recent_log.json: {log_file}")
        
        # 2. Lấy batch data
        print("\n📊 Fetching batch data...")
        active_batch, context_msgs = await recent_log_service.get_batch_for_processing()
        
        if not active_batch:
            print("⚠️ No active batch to process")
            print("Tip: Thêm ít nhất 10 messages vào recent_log để test")
            return
        
        print(f"✅ Active Batch: {len(active_batch)} messages")
        print(f"✅ Context: {len(context_msgs)} messages")
        
        # Show sample messages
        print("\n📝 Sample Messages from Batch:")
        for i, msg in enumerate(active_batch[:3], 1):
            print(f"  {i}. [{msg.username}]: {msg.content[:50]}...")
        
        # 3. Chạy batch processing
        print("\n🤖 Running AI Analysis...")
        print("⏳ This may take 10-15 seconds...")
        
        await batch_processor.process_batch(server_id="1067690340359880724")
        
        print("\n✅ Batch processing completed!")
        
        # 4. Kiểm tra kết quả
        print("\n📁 Checking for created UserSummary files...")
        user_profiles_dir = project_root / "data" / "user_profiles"
        
        if user_profiles_dir.exists():
            profiles = list(user_profiles_dir.glob("*/summary.json"))
            if profiles:
                print(f"✅ Found {len(profiles)} UserSummary files:")
                for profile in profiles:
                    user_id = profile.parent.name
                    print(f"  - {user_id}/summary.json")
            else:
                print("⚠️ No UserSummary files created (no critical events detected)")
        else:
            print("⚠️ user_profiles directory doesn't exist yet")
        
        # 5. Check pending updates
        print("\n📨 Checking pending updates...")
        pending_file = project_root / "data" / "system" / "pending_updates.json"
        if pending_file.exists():
            import json
            with open(pending_file, 'r') as f:
                pending_data = json.load(f)
                if pending_data.get("queue"):
                    print(f"✅ Found pending updates for {len(pending_data['queue'])} users")
                else:
                    print("ℹ️ No pending updates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting batch processing test...\n")
    asyncio.run(test_batch_processing())
