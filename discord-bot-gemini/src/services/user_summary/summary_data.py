import os
import json
import logging
import time
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class SummaryDataManager:
    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300

    def __init__(self):
        # Always resolve to src/data/user_summaries
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.summaries_dir = os.path.join(base_dir, "data", "user_summaries")
        os.makedirs(self.summaries_dir, exist_ok=True)

        # In-memory cache: {user_id: (data, timestamp)}
        self._summary_cache: Dict[str, Tuple[str, float]] = {}
        self._history_cache: Dict[str, Tuple[List[Dict], float]] = {}

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid based on TTL"""
        return (time.time() - timestamp) < self.CACHE_TTL

    def get_user_history(self, user_id: str) -> List[Dict]:
        # Check cache first
        if user_id in self._history_cache:
            cached_data, timestamp = self._history_cache[user_id]
            if self._is_cache_valid(timestamp):
                return cached_data

        # Cache miss - read from file
        history_file = os.path.join(self.summaries_dir, f"{user_id}_history.json")
        if not os.path.exists(history_file):
            return []
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            if not isinstance(history, list):
                logger.error(f"History file format invalid for {user_id}")
                return []
            # Update cache
            self._history_cache[user_id] = (history, time.time())
            return history
        except Exception as e:
            logger.error(f"Error loading history for {user_id}: {e}")
            return []

    def get_user_summary(self, user_id: str) -> str:
        # Check cache first
        if user_id in self._summary_cache:
            cached_data, timestamp = self._summary_cache[user_id]
            if self._is_cache_valid(timestamp):
                return cached_data

        # Cache miss - read from file
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.json")
        if not os.path.exists(summary_file):
            return ""
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                summary_str = json.dumps(data, ensure_ascii=False, indent=2)
            # Update cache
            self._summary_cache[user_id] = (summary_str, time.time())
            return summary_str
        except Exception as e:
            logger.error(f"Error loading summary for {user_id}: {e}")
            return ""

    def save_user_summary(self, user_id: str, summary: str):
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.json")
        try:
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)

            # Try to parse summary as JSON if it's a string
            if isinstance(summary, str):
                try:
                    data = json.loads(summary)
                except json.JSONDecodeError:
                    data = {"raw_content": summary}
            else:
                data = summary

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Update cache after save
            summary_str = json.dumps(data, ensure_ascii=False, indent=2)
            self._summary_cache[user_id] = (summary_str, time.time())

            logger.info(f"Summary saved for user {user_id}")

        except Exception as e:
            logger.error(f"Error saving summary for {user_id}: {e}")

    def invalidate_history_cache(self, user_id: str):
        """Invalidate history cache for a user (call after saving new history)"""
        if user_id in self._history_cache:
            del self._history_cache[user_id]

    def clear_user_summary(self, user_id: str):
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.json")
        txt_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        try:
            if os.path.exists(summary_file):
                os.remove(summary_file)
            if os.path.exists(txt_file):
                os.remove(txt_file)
            # Clear cache
            if user_id in self._summary_cache:
                del self._summary_cache[user_id]
            logger.info(f"Summary cleared for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing summary for {user_id}: {e}")
