"""
Populate recent_log với test data có critical events rõ ràng
"""
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.conversation.recent_log_service import recent_log_service

async def main():
    print("📝 Adding test messages with clear critical events...\n")
    
    server_id = "1067690340359880724"
    
    # Test messages với critical info
    test_messages = [
        ("726302130318868500", "flowerf", "Chào mọi người!"),
        ("726302130318868500", "flowerf", "Tên mình là Hòa nha"),
        ("726302130318868500", "flowerf", "Mình 25 tuổi, đang sống ở Hà Nội"),
        ("418621389449199616", "BeBay", "Chào Hòa! Mình là Bảy đây"),
        ("726302130318868500", "flowerf", "Mình đang học Python và làm Discord bot"),
        ("418621389449199616", "BeBay", "Ồ hay đấy! Mình cũng thích Python"),
        ("726302130318868500", "flowerf", "Mình thích chơi game và coding"),
        ("418621389449199616", "BeBay", "Hay là chúng ta hợp tác làm project bot này nhé?"),
        ("726302130318868500", "flowerf", "Được nha! Mình đang làm với Ollama + Gemini AI"),
        ("418621389449199616", "BeBay", "Perfect! Mình sẽ giúp phần backend"),
    ]
    
    # Add messages
    for user_id, username, content in test_messages:
        await recent_log_service.add_activity(
            user_id=user_id,
            username=username,
            content=content,
            channel_id="test_channel",
            server_id=server_id,
            action="message",
            mentioned_users=[]
        )
        print(f"✅ Added: [{username}] {content[:40]}...")
    
    print(f"\n✅ Added {len(test_messages)} test messages")
    print("🎯 These messages contain:")
    print("  - Name reveal (Hòa)")
    print("  - Age & location (25, Hà Nội)")
    print("  - Interests (Python, gaming, coding)")
    print("  - New relationship (collaboration between Hòa and Bảy)")
    print("  - Life event (working on bot project)")
    print("\n💡 Now run: python scripts/test_batch_simple.py")

if __name__ == "__main__":
    asyncio.run(main())
