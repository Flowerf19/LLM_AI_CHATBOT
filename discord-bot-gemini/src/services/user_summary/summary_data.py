import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SummaryDataManager:
    def __init__(self):
        # Always resolve to src/data/user_summaries
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.summaries_dir = os.path.join(base_dir, 'data', 'user_summaries')
        os.makedirs(self.summaries_dir, exist_ok=True)

    def get_user_history(self, user_id: str) -> List[Dict]:
        history_file = os.path.join(self.summaries_dir, f"{user_id}_history.json")
        if not os.path.exists(history_file):
            return []
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            if not isinstance(history, list):
                logger.error(f"History file format invalid for {user_id}")
                return []
            return history
        except Exception as e:
            logger.error(f"Error loading history for {user_id}: {e}")
            return []

    def get_user_summary(self, user_id: str) -> str:
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        if not os.path.exists(summary_file):
            return ""
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading summary for {user_id}: {e}")
            return ""

    def save_user_summary(self, user_id: str, summary: str):
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        try:
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary.strip())
            logger.info(f"Summary saved for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving summary for {user_id}: {e}")

    def clear_user_summary(self, user_id: str):
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        try:
            if os.path.exists(summary_file):
                os.remove(summary_file)
                logger.info(f"Summary cleared for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing summary for {user_id}: {e}") 