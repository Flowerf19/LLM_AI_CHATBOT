import os
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class RelationshipDataManager:
    def __init__(self):
        # Always resolve to src/data/relationships
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(base_dir, 'data', 'relationships')
        self.relationships_file = os.path.join(self.data_dir, 'relationships.json')
        self.user_names_file = os.path.join(self.data_dir, 'user_names.json')
        self.interactions_file = os.path.join(self.data_dir, 'interactions.json')
        self.conversation_history_file = os.path.join(self.data_dir, 'conversation_history.json')

    def load_json(self, file_path: str) -> Dict:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}

    def save_json(self, file_path: str, data: Dict):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")

    def load_relationships(self) -> Dict:
        return self.load_json(self.relationships_file)

    def save_relationships(self, relationships: Dict):
        self.save_json(self.relationships_file, relationships)

    def load_user_names(self) -> Dict:
        return self.load_json(self.user_names_file)

    def save_user_names(self, user_names: Dict):
        self.save_json(self.user_names_file, user_names)

    def load_interactions(self) -> Dict:
        return self.load_json(self.interactions_file)

    def save_interactions(self, interactions: Dict):
        self.save_json(self.interactions_file, interactions)

    def load_conversation_history(self) -> Dict:
        return self.load_json(self.conversation_history_file)

    def save_conversation_history(self, conversation_history: Dict):
        self.save_json(self.conversation_history_file, conversation_history) 