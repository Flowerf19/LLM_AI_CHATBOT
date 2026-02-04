"""
Service để quản lý Pending Updates (Lazy Sync Queue)
Xử lý việc đồng bộ relationship giữa các user khi có user offline
"""
from typing import List
from datetime import datetime

from src.models.v2.sync import SyncQueue, PendingUpdate
from src.data.data_manager import data_manager
from src.utils.helpers import get_logger

logger = get_logger(__name__)

PENDING_UPDATES_PATH = "data/system/pending_updates.json"


class PendingUpdateService:
    """
    Quản lý queue của các updates đang chờ xử lý.
    Dùng khi User B offline mà User A có relationship event liên quan đến B.
    """
    
    def __init__(self):
        self.file_path = PENDING_UPDATES_PATH

    async def _load_queue(self, server_id: str = "default") -> SyncQueue:
        """Load queue hiện tại"""
        def default_factory():
            return SyncQueue(server_id=server_id)
        
        return await data_manager.load_model(self.file_path, SyncQueue, default_factory=default_factory)

    async def add_pending_update(
        self, 
        target_user_id: str,
        source_event_id: str,
        update_type: str,
        data: dict,
        server_id: str = "default"
    ):
        """
        Thêm một pending update vào queue.
        
        Args:
            target_user_id: User cần được update (đang offline)
            source_event_id: ID của event gây ra update này
            update_type: Loại update ("relationship_sync", "mention_sync")
            data: Dict chứa thông tin update
            server_id: Server ID
        """
        queue = await self._load_queue(server_id)
        queue.server_id = server_id
        
        # Tạo pending update mới
        pending = PendingUpdate(
            target_user_id=target_user_id,
            source_event_id=source_event_id,
            update_type=update_type,
            data=data,
            created_at=datetime.now()
        )
        
        # Thêm vào queue của target user
        if target_user_id not in queue.queue:
            queue.queue[target_user_id] = []
        
        queue.queue[target_user_id].append(pending)
        queue.last_processed = datetime.now()
        
        await data_manager.save_model(self.file_path, queue)
        logger.info(f"Added pending update for user {target_user_id}: {update_type}")

    async def get_pending_updates(self, user_id: str, server_id: str = "default") -> List[PendingUpdate]:
        """
        Lấy tất cả pending updates cho một user.
        Thường gọi khi user vừa online/chat.
        
        Returns:
            List[PendingUpdate]: Danh sách các update chờ xử lý
        """
        queue = await self._load_queue(server_id)
        return queue.queue.get(user_id, [])

    async def clear_pending_updates(self, user_id: str, server_id: str = "default"):
        """
        Xóa tất cả pending updates của một user sau khi đã xử lý xong.
        
        Args:
            user_id: User ID cần clear
            server_id: Server ID
        """
        queue = await self._load_queue(server_id)
        
        if user_id in queue.queue:
            count = len(queue.queue[user_id])
            del queue.queue[user_id]
            queue.last_processed = datetime.now()
            
            await data_manager.save_model(self.file_path, queue)
            logger.info(f"Cleared {count} pending updates for user {user_id}")

    async def has_pending_updates(self, user_id: str, server_id: str = "default") -> bool:
        """
        Kiểm tra xem user có pending updates không.
        
        Returns:
            bool: True nếu có updates đang chờ
        """
        queue = await self._load_queue(server_id)
        return user_id in queue.queue and len(queue.queue[user_id]) > 0


# Global instance
pending_update_service = PendingUpdateService()
