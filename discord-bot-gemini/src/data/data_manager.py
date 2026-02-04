import json
import aiofiles
import asyncio
import os
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from src.utils.helpers import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class JsonDataManager:
    """
    Quản lý việc Đọc/Ghi file JSON an toàn với Async Lock.
    Tự động convert giữa JSON và Pydantic Model.
    """
    def __init__(self):
        self._locks = {}  # Map file_path -> Lock

    def _get_lock(self, file_path: str) -> asyncio.Lock:
        if file_path not in self._locks:
            self._locks[file_path] = asyncio.Lock()
        return self._locks[file_path]

    async def save_model(self, file_path: str, model: BaseModel):
        """Lưu Pydantic model xuống file JSON"""
        lock = self._get_lock(file_path)
        async with lock:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    # model_dump_json() của Pydantic V2 (hoặc .json() nếu V1)
                    await f.write(model.model_dump_json(indent=2))
            except Exception as e:
                logger.error(f"Failed to save {file_path}: {e}")
                raise

    async def load_model(self, file_path: str, model_cls: Type[T], default_factory=None) -> T:
        """Đọc file JSON và parse thành Pydantic Model"""
        lock = self._get_lock(file_path)
        async with lock:
            if not os.path.exists(file_path):
                if default_factory:
                    return default_factory()
                # Nếu không có default factory, trả về model rỗng (nếu model cho phép)
                # Hoặc raise error tùy logic. Ở đây ta return instance mặc định của model
                return model_cls()

            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if not content.strip():
                        return default_factory() if default_factory else model_cls()
                    
                    return model_cls.model_validate_json(content)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                return default_factory() if default_factory else model_cls()

# Global instance
data_manager = JsonDataManager()