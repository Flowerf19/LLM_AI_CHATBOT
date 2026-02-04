from datetime import datetime, timedelta
from typing import List, Tuple

from src.models.v2.recent_log import RecentLog, Activity
from src.data.data_manager import data_manager
from src.utils.helpers import get_logger

logger = get_logger(__name__)

RECENT_LOG_PATH = "data/recent_log.json"
BATCH_SIZE_TRIGGER = 10
TIME_FLUSH_MINUTES = 30

class RecentLogService:
    def __init__(self):
        self.file_path = RECENT_LOG_PATH

    async def _load_log(self) -> RecentLog:
        """Load log hiện tại, nếu chưa có thì tạo mới"""
        def default_factory():
            return RecentLog(server_id="default") # Server ID sẽ được update khi save
        
        return await data_manager.load_model(self.file_path, RecentLog, default_factory=default_factory)

    async def add_activity(self, 
                           user_id: str, 
                           username: str, 
                           content: str, 
                           channel_id: str,
                           server_id: str,
                           action: str = "message", 
                           mentioned_users: List[str] = None) -> bool:
        """
        Thêm message mới vào log.
        Return True nếu cần Trigger Batch Processing (đủ 10 tin hoặc timeout).
        """
        log = await self._load_log()
        
        # Update server info
        log.server_id = server_id
        log.last_updated = datetime.now()

        # Tạo activity mới
        new_activity = Activity(
            user_id=user_id,
            username=username,
            action=action,
            content=content,
            channel_id=channel_id,
            mentioned_users=mentioned_users or [],
            timestamp=datetime.now(),
            is_context_only=False
        )

        # Append & Sliding Window (Giữ 100 tin mới nhất)
        log.messages.append(new_activity)
        if len(log.messages) > log.max_messages:
            log.messages = log.messages[-log.max_messages:]  # Cắt bớt tin cũ

        # --- Batch Logic ---
        batch = log.batch_tracking
        batch.current_batch_size += 1
        
        # Logic Time Flush: Nếu đây là tin nhắn đầu tiên của batch, đánh dấu thời gian
        if batch.current_batch_size == 1:
            batch.first_msg_in_batch_at = datetime.now()

        should_trigger = False
        
        # Rule 1: Đủ số lượng
        if batch.current_batch_size >= BATCH_SIZE_TRIGGER:
            logger.info(f"Trigger Batch: Size Limit ({batch.current_batch_size})")
            should_trigger = True
        
        # Rule 2: Time Flush (Quá 30p kể từ tin đầu tiên trong batch)
        elif batch.first_msg_in_batch_at:
            time_diff = datetime.now() - batch.first_msg_in_batch_at
            if time_diff > timedelta(minutes=TIME_FLUSH_MINUTES):
                logger.info(f"Trigger Batch: Time Flush ({time_diff})")
                should_trigger = True

        await data_manager.save_model(self.file_path, log)
        return should_trigger

    async def get_batch_for_processing(self) -> Tuple[List[Activity], List[Activity]]:
        """
        Lấy data để gửi cho AI xử lý.
        Return: (current_batch, context_messages)
        - current_batch: Các tin nhắn chưa được xử lý (active)
        - context_messages: 5 tin nhắn ngay trước đó (để gối đầu context)
        """
        log = await self._load_log()
        batch_size = log.batch_tracking.current_batch_size
        
        if batch_size == 0:
            return [], []

        # Lấy batch hiện tại (các tin cuối cùng)
        current_batch = log.messages[-batch_size:]
        
        # Lấy context (5 tin trước batch này)
        # Index của tin đầu tiên trong batch là: len - batch_size
        start_idx = len(log.messages) - batch_size
        context_end_idx = start_idx
        context_start_idx = max(0, context_end_idx - 5)
        
        context_messages = log.messages[context_start_idx:context_end_idx]
        
        # Đánh dấu context message là read-only (chỉ phòng hờ logic UI)
        for msg in context_messages:
            msg.is_context_only = True
            
        return current_batch, context_messages

    async def reset_batch_tracker(self):
        """Reset bộ đếm sau khi AI xử lý xong"""
        log = await self._load_log()
        log.batch_tracking.current_batch_size = 0
        log.batch_tracking.first_msg_in_batch_at = None
        log.batch_tracking.total_batches_processed += 1
        log.batch_tracking.last_summary_at = datetime.now()
        
        await data_manager.save_model(self.file_path, log)

    async def get_recent_context(self, limit: int = 20) -> str:
        """
        Lấy context dạng text cho Chatbot trả lời user (không phải để summarize).
        Lấy N tin nhắn gần nhất bất kể batch.
        """
        log = await self._load_log()
        msgs = log.messages[-limit:]
        
        context_str = ""
        for msg in msgs:
            time_str = msg.timestamp.strftime("%H:%M")
            context_str += f"[{time_str}] {msg.username}: {msg.content}\n"
            
        return context_str

recent_log_service = RecentLogService()