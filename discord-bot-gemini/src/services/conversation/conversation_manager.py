import logging
from datetime import datetime
from typing import List, Dict, Set
import json
from config.settings import Config

logger = logging.getLogger('discord_bot.ConversationManager')

class ConversationManager:
    """Manages conversation locks, queuing, and history"""
    
    def __init__(self):
        # Changed from single user lock to set of active users for concurrency
        self.active_users: Set[str] = set()
        self.user_lock_times: Dict[str, datetime] = {}
        
        self.pending_messages: List[Dict] = []
        self.conversation_history = {}
        self.max_history_length = 10
    
    def set_conversation_lock(self, user_id: str):
        """Lock conversation for a specific user"""
        self.active_users.add(user_id)
        self.user_lock_times[user_id] = datetime.utcnow()
        logger.info(f"🔒 Conversation locked for user {user_id}")
    
    def release_conversation_lock(self, user_id: str):
        """Release conversation lock for a specific user"""
        if user_id in self.active_users:
            self.active_users.discard(user_id)
            self.user_lock_times.pop(user_id, None)
            logger.info(f"🔓 Conversation unlocked for user {user_id}")
    
    def is_conversation_locked(self, user_id: str) -> bool:
        """Check if conversation is locked for this specific user"""
        # Now we only check if THIS user is already being processed
        # We don't block other users anymore
        return user_id in self.active_users
    
    def get_lock_duration(self, user_id: str) -> int:
        """Get how long conversation has been locked for a user (in seconds)"""
        if user_id in self.user_lock_times:
            return int((datetime.utcnow() - self.user_lock_times[user_id]).total_seconds())
        return 0
    
    def add_to_pending_queue(self, message, content: str):
        """Add message to pending queue"""
        self.pending_messages.append({
            'message': message,
            'content': content,
            'timestamp': datetime.utcnow()
        })
        logger.info(f"⏳ User {message.author.id} added to pending queue")
    
    def clear_pending_queue(self) -> int:
        """Clear pending queue and return count"""
        count = len(self.pending_messages)
        self.pending_messages.clear()
        return count
    
    def add_to_history(self, user_id: str, user_message: str, bot_response: str):
        """Add conversation to in-memory history"""
        timestamp = datetime.utcnow().isoformat()
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': timestamp
        })
        
        # Keep only recent history in memory
        if len(self.conversation_history[user_id]) > self.max_history_length:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length:]
    
    def get_conversation_context(self, user_id: str) -> str:
        """Get recent conversation context"""
        if user_id not in self.conversation_history:
            return ""
        
        context_parts = []
        for entry in self.conversation_history[user_id][-3:]:  # Last 3 exchanges
            context_parts.append(f"User: {entry['user']}")
            context_parts.append(f"Bot: {entry['bot']}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def save_to_persistent_history(self, user_id: str, user_message: str, bot_response: str):
        """Save conversation to persistent file storage"""
        try:
            history_dir = Config.USER_SUMMARIES_DIR
            history_file = history_dir / f"{user_id}_history.json"
            
            history_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().isoformat()
            
            # Load existing history
            history = []
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except Exception as e:
                    logger.error(f"❌ Error loading existing history: {e}")
                    history = []
            
            # Add new messages
            history.extend([
                {
                    'role': 'user',
                    'content': user_message,
                    'timestamp': timestamp
                },
                {
                    'role': 'assistant',
                    'content': bot_response,
                    'timestamp': timestamp
                }
            ])
            
            # Keep only recent history
            if len(history) > 100:
                history = history[-100:]
                
            # Save back to file
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 Saved conversation history for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error saving persistent history for {user_id}: {e}")
    
    def get_queue_status(self) -> dict:
        """Get queue status information"""
        pending_users = [pm['message'].author.id for pm in self.pending_messages[-3:]]
        return {
            'active_users_count': len(self.active_users),
            'pending_count': len(self.pending_messages),
            'pending_users': pending_users
        }