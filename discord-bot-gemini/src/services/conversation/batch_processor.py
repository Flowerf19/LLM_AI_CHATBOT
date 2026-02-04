"""
BatchProcessor - Xử lý batch tin nhắn và gửi cho AI tóm tắt
V2.1: Tích hợp Context Overlap để đảm bảo tính liên tục giữa các batch
"""
import json
from datetime import datetime
from typing import List
from pathlib import Path

from src.utils.helpers import get_logger
from src.data.data_manager import data_manager
from src.services.conversation.recent_log_service import recent_log_service
from src.services.conversation.pending_update_service import pending_update_service
from src.services.ai.ollama_service import OllamaService 
from src.services.ai.gemini_service import GeminiService
from src.config.settings import Config

from src.models.v2.recent_log import Activity
from src.models.v2.batch_summary import BatchSummary, CriticalEvent
from src.models.v2.user_summary import UserSummary, CriticalEventHistory

logger = get_logger(__name__)

# Use absolute path relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
USER_PROFILE_DIR = str(PROJECT_ROOT / "data" / "user_profiles")
PROMPT_PATH = Config.PROMPTS_DIR / "batch_summary_prompt.json"


class BatchProcessor:
    """
    Xử lý batch tin nhắn với Context Overlap (V2.1):
    1. Lấy batch + context từ RecentLog
    2. Format data cho AI với context overlap
    3. Gọi AI để tóm tắt và phát hiện critical events
    4. Xử lý critical events và Lazy Sync
    """
    
    def __init__(self):
        # Chọn AI service dựa vào config
        ai_provider = getattr(Config, 'ai_provider', 'ollama').lower()
        self.ai_service = GeminiService() if ai_provider == 'gemini' else OllamaService()
        self._prompt_template = None

    async def _load_prompt(self):
        if not self._prompt_template:
            try:
                async with data_manager._get_lock(str(PROMPT_PATH)):
                    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                        self._prompt_template = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load prompt template: {e}")
                # Fallback prompt cực kỳ cơ bản nếu file lỗi
                self._prompt_template = {
                    "system": "You are a JSON summarizer.",
                    "format": "{}"
                }

    async def process_batch(self, server_id: str = "default"):
        """
        Main Flow V2.1:
        1. Lấy tin nhắn từ RecentLog (batch + context overlap)
        2. Gửi cho AI phân tích với context
        3. Nếu có Critical Event -> Update vào UserSummary + Lazy Sync
        4. Reset Batch Tracker
        """
        # 1. Lấy dữ liệu với context overlap
        active_batch, context_msgs = await recent_log_service.get_batch_for_processing()
        
        if not active_batch:
            logger.debug("No batch to process")
            return

        logger.info(f"🔄 Processing batch: {len(active_batch)} messages + {len(context_msgs)} context")
        
        # 2. Chuẩn bị Prompt với Context Overlap
        await self._load_prompt()
        full_prompt = self._build_prompt_with_context(context_msgs, active_batch)

        # 3. Gọi AI
        try:
            raw_response = await self.ai_service.generate(full_prompt)
            
            # Clean response (gỡ markdown ```json ... ``` nếu có)
            clean_json = self._extract_json(raw_response)
            parsed_data = json.loads(clean_json)
            
            # Debug: Log AI response
            logger.debug(f"🤖 AI Response: {parsed_data.get('summary', 'N/A')}")
            logger.debug(f"🔍 Detected Events: {len(parsed_data.get('critical_events', []))}")
            
            # Validate bằng Pydantic
            batch_summary = BatchSummary(
                batch_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                messages_count=len(active_batch),
                user_ids=list(set([msg.user_id for msg in active_batch])),
                ai_summary=parsed_data.get("summary", ""),
                has_critical_events=parsed_data.get("has_critical_events", False),
                critical_events=[
                    CriticalEvent(**evt) for evt in parsed_data.get("critical_events", [])
                ],
                processing_time=0.0,
                llm_model=self.ai_service.__class__.__name__
            )
            
            logger.info(f"✅ AI Analysis complete. Critical Events: {len(batch_summary.critical_events)}")
            if batch_summary.critical_events:
                for evt in batch_summary.critical_events:
                    logger.info(f"  📌 {evt.event_type}: {evt.summary} (confidence: {evt.confidence})")

            # 4. Xử lý Critical Events với Lazy Sync (V2.1)
            if batch_summary.has_critical_events:
                await self._handle_critical_events(
                    batch_summary.critical_events, 
                    batch_summary.batch_id,
                    server_id
                )

        except Exception as e:
            logger.error(f"❌ Batch AI Error: {e}", exc_info=True)
        
        # 5. Reset Tracker (quan trọng để không bị kẹt)
        await recent_log_service.reset_batch_tracker()
    
    def _build_prompt_with_context(
        self, 
        context_messages: List[Activity], 
        current_batch: List[Activity]
    ) -> str:
        """
        Xây dựng prompt cho AI với Context Overlap (V2.1).
        Format: Context (read-only) + Current Batch (analyze)
        """
        # Format context messages
        context_text = ""
        if context_messages:
            context_text = "--- CONTEXT (READ ONLY) ---\n"
            context_text += "These are previous messages for context:\n"
            for msg in context_messages:
                time_str = msg.timestamp.strftime("%H:%M")
                context_text += f"[{time_str}] {msg.username}: {msg.content}\n"
            context_text += "\n"
        
        # Format current batch
        batch_text = "--- MESSAGES TO ANALYZE ---\n"
        for msg in current_batch:
            time_str = msg.timestamp.strftime("%H:%M")
            batch_text += f"[{time_str}] {msg.username} ({msg.user_id}): {msg.content}\n"
        
        # Build full prompt
        full_prompt = (
            f"{self._prompt_template.get('instruction', 'Analyze these messages')}\n\n"
            f"{context_text}"
            f"{batch_text}\n"
            f"--- OUTPUT FORMAT ---\n{json.dumps(self._prompt_template.get('format_example', {}), indent=2)}"
        )
        
        return full_prompt
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON từ text, xử lý markdown code blocks nếu có"""
        text = text.strip()
        
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        
        return text

    async def _handle_critical_events(
        self, 
        events: List[CriticalEvent], 
        batch_id: str,
        server_id: str = "default"
    ):
        """
        Update UserSummary dựa trên sự kiện quan trọng.
        V2.1: Tích hợp Lazy Sync - tạo pending updates cho affected users
        """
        for event in events:
            user_id = event.user_id
            if not user_id: 
                continue

            # Load User Profile
            profile_path = f"{USER_PROFILE_DIR}/{user_id}/summary.json"
            
            def default_user():
                return UserSummary(user_id=user_id, username=event.username)

            user_summary = await data_manager.load_model(
                profile_path, 
                UserSummary, 
                default_factory=default_user
            )

            # Convert to History Event
            history_event = CriticalEventHistory(
                event_id=f"evt_{int(datetime.now().timestamp())}",
                timestamp=event.timestamp,
                event_type=event.event_type,
                summary=event.summary,
                confidence=event.confidence,
                batch_id=batch_id,
                detected_at=datetime.now(),
                status="active",
                affected_relationships=event.affected_users
            )
            
            # Update & Save User A (người tạo event)
            user_summary.critical_events.append(history_event)
            user_summary.last_updated = datetime.now()
            user_summary.total_events_tracked += 1
            
            await data_manager.save_model(profile_path, user_summary)
            logger.info(f"💾 Updated UserSummary for {event.username}: {event.event_type}")
            
            # V2.1: Lazy Sync - Tạo pending updates cho affected users
            if event.affected_users:
                for affected_user_id in event.affected_users:
                    if affected_user_id != user_id:  # Không tạo pending cho chính mình
                        await pending_update_service.add_pending_update(
                            target_user_id=affected_user_id,
                            source_event_id=history_event.event_id,
                            update_type="relationship_sync",
                            data={
                                "from_user_id": user_id,
                                "from_username": event.username,
                                "event_type": event.event_type,
                                "summary": event.summary,
                                "timestamp": event.timestamp.isoformat()
                            },
                            server_id=server_id
                        )
                        logger.info(f"📌 Created pending update for user {affected_user_id}")

# Global instance
batch_processor = BatchProcessor()