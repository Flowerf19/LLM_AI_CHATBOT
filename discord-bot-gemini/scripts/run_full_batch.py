"""Run full batch processor và tạo UserSummary files"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.conversation.batch_processor import batch_processor

async def main():
    print("🚀 Running FULL batch processor...")
    print("⏳ This will take 60-90 seconds with Ollama...\n")
    
    try:
        await batch_processor.process_batch("1067690340359880724")
        
        print("\n✅ Batch processing completed!")
        print("\n📁 Checking created files...")
        
        # Check user_profiles
        profiles_dir = project_root / "data" / "user_profiles"
        if profiles_dir.exists():
            profiles = list(profiles_dir.glob("*/summary.json"))
            print(f"\n✅ Created {len(profiles)} UserSummary files:")
            for p in profiles:
                print(f"  - {p}")
        else:
            print("\n⚠️ No user_profiles directory created")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
