"""
Simple test - Chạy batch processing và show AI raw response
"""
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.conversation.recent_log_service import recent_log_service
from src.services.ai.ollama_service import OllamaService
from src.config.settings import Config
import json

async def main():
    print("🧪 SIMPLE BATCH TEST\n")
    
    # 1. Get batch data
    print("📊 Loading batch...")
    active_batch, context = await recent_log_service.get_batch_for_processing()
    
    if not active_batch:
        print("❌ No batch data. Need at least 10 messages in recent_log.json")
        return
    
    print(f"✅ Batch: {len(active_batch)} messages")
    print(f"✅ Context: {len(context)} messages\n")
    
    # Show messages
    print("📝 Messages in batch:")
    for i, msg in enumerate(active_batch[:5], 1):
        content = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
        print(f"  {i}. [{msg.username}]: {content}")
    print()
    
    # 2. Load prompt
    prompt_file = Config.PROMPTS_DIR / "batch_summary_prompt.json"
    with open(prompt_file, 'r') as f:
        prompt_data = json.load(f)
    
    # 3. Build simple prompt
    messages_text = "\n".join([
        f"[{msg.timestamp.strftime('%H:%M')}] {msg.username}: {msg.content}"
        for msg in active_batch
    ])
    
    prompt = f"""{prompt_data['instruction']}

Messages to analyze:
{messages_text}

Return JSON with format: {json.dumps(prompt_data['format_example'], indent=2)}
"""
    
    # 4. Call AI
    print("🤖 Calling Ollama AI...")
    print("⏳ Waiting for response (timeout: 90s)...\n")
    
    try:
        ai_service = OllamaService()
        response = await asyncio.wait_for(
            ai_service.generate(prompt),
            timeout=90.0
        )
        
        print("=" * 70)
        print("📄 AI RAW RESPONSE:")
        print("=" * 70)
        print(response)
        print("=" * 70)
        
        # Try to parse
        print("\n🔍 Parsing JSON...")
        # Remove markdown if exists
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response)
        
        print(f"\n✅ Summary: {data.get('summary', 'N/A')}")
        print(f"✅ Has Critical Events: {data.get('has_critical_events', False)}")
        print(f"✅ Events Count: {len(data.get('critical_events', []))}")
        
        if data.get('critical_events'):
            print("\n📌 Critical Events Detected:")
            for evt in data['critical_events']:
                print(f"  - {evt['event_type']}: {evt['summary']} (conf: {evt['confidence']})")
        
    except asyncio.TimeoutError:
        print("❌ Timeout! AI took too long to respond.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
