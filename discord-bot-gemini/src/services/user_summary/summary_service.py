"""
SummaryService - Orchestrates user summary operations.

Responsibilities:
    - Coordinate between data access (SummaryDataManager) and parsing (SummaryParser)
    - Business logic for when/how to update summaries
    - Generate summaries via AI service

Dependencies:
    - SummaryDataManager: Handles JSON file I/O
    - SummaryParser: Handles text parsing/merging
"""
import os
import json
import logging
import time
from typing import Optional
from discord import Message, Client

from config.settings import Config
from services.user_summary.summary_data import SummaryDataManager
from services.user_summary.summary_parser import SummaryParser

logger = logging.getLogger(__name__)


class SummaryService:
    """
    Service for managing user summaries.
    Uses repository pattern for data access and delegates parsing to SummaryParser.
    """
    
    # Thresholds for summary updates
    MESSAGE_THRESHOLD = 8          # Messages before considering update
    TIME_THRESHOLD = 1800          # Seconds (30 min) before considering update
    TEMPLATE_MESSAGE_THRESHOLD = 3 # For template summaries, update faster
    
    def __init__(self, bot: Optional[Client] = None):
        self.bot = bot
        self.data_manager = SummaryDataManager()
        self.parser = SummaryParser()
        
        # Track last update per user
        self._last_update_time: dict[str, float] = {}
        self._message_count_since_update: dict[str, int] = {}

    # =========================================================================
    # Public API - Summary Operations
    # =========================================================================
    
    def get_user_summary(self, user_id: str) -> str:
        """Get user summary. Delegates to data manager."""
        return self.data_manager.get_user_summary(user_id)

    def save_user_summary(self, user_id: str, summary: str):
        """Save user summary. Delegates to data manager."""
        self.data_manager.save_user_summary(user_id, summary)

    def clear_user_summary(self, user_id: str):
        """Clear user summary. Delegates to data manager."""
        self.data_manager.clear_user_summary(user_id)

    def get_user_history(self, user_id: str):
        """Get user conversation history. Delegates to data manager."""
        return self.data_manager.get_user_history(user_id)

    # =========================================================================
    # Public API - Smart Update Logic
    # =========================================================================
    
    def should_update_summary(self, user_id: str, current_message: Optional[Message] = None) -> bool:
        """
        Determine if a summary update should be triggered.
        
        Returns True if:
            - Message threshold reached (based on history file)
            - Time threshold reached
            - Summary is a template (unfilled)
            - No summary exists yet
        """
        current_summary = self.get_user_summary(user_id)
        
        # No summary - should create one
        if not current_summary:
            logger.debug(f"No summary for {user_id}, should update")
            return True
        
        # Get message count from persistent history (not in-memory counter)
        history = self.get_user_history(user_id)
        # Count only user messages in history
        user_msg_count = len([m for m in history if m.get("role") == "user"]) if history else 0
        
        # Template summary - update faster
        if self.parser.is_template_summary(current_summary):
            if user_msg_count >= self.TEMPLATE_MESSAGE_THRESHOLD:
                logger.debug(f"Template summary for {user_id}, user_msg_count={user_msg_count}")
                return True
        
        # Check message threshold (using in-memory counter for session tracking)
        session_msg_count = self._message_count_since_update.get(user_id, 0)
        if session_msg_count >= self.MESSAGE_THRESHOLD:
            logger.debug(f"Session message threshold reached for {user_id}: {session_msg_count}")
            return True
        
        # Check time threshold
        last_update = self._last_update_time.get(user_id, 0)
        time_since = time.time() - last_update
        if last_update > 0 and time_since >= self.TIME_THRESHOLD:
            logger.debug(f"Time threshold reached for {user_id}: {time_since:.0f}s")
            return True
        
        return False

    def increment_message_count(self, user_id: str):
        """Increment the message count for a user."""
        current = self._message_count_since_update.get(user_id, 0)
        self._message_count_since_update[user_id] = current + 1

    def reset_update_tracking(self, user_id: str):
        """Reset tracking counters after a successful update."""
        self._message_count_since_update[user_id] = 0
        self._last_update_time[user_id] = time.time()

    # =========================================================================
    # AI-Powered Summary Generation
    # =========================================================================

    async def update_summary_smart(
        self,
        user_id: str,
        ai_service,
        recent_messages: list = None,
        force: bool = False
    ) -> Optional[str]:
        """
        Generate or update user summary using AI.
        
        Args:
            user_id: User identifier
            ai_service: AI service (Gemini/DeepSeek) for generation
            recent_messages: Recent conversation messages
            force: Force update regardless of thresholds
        
        Returns:
            New summary string if updated, None otherwise
        """
        if not force and not self.should_update_summary(user_id):
            return None
        
        try:
            # Get current summary and history
            current_summary = self.get_user_summary(user_id)
            history = recent_messages or self.get_user_history(user_id)
            
            if not history:
                logger.debug(f"No history for {user_id}, skipping summary update")
                return None
            
            # Build prompt for AI
            prompt = self._build_summary_prompt(current_summary, history)
            
            # Generate new summary via AI (use generate_summary method for raw prompt)
            # Check if ai_service has generate_summary method, otherwise fall back to generate_response
            if hasattr(ai_service, 'generate_summary'):
                new_summary_text = await ai_service.generate_summary(prompt)
            else:
                new_summary_text = await ai_service.generate_response(prompt)
            
            logger.debug(f"AI response for {user_id}: {new_summary_text[:500] if new_summary_text else 'None'}...")
            
            if not new_summary_text or new_summary_text.startswith("Error"):
                logger.warning(f"AI returned empty or error summary for {user_id}: {new_summary_text}")
                return None
            
            # Merge with existing summary (preserves old data)
            if current_summary:
                logger.debug(f"Merging summary for {user_id}")
                merged_summary = self.parser.merge_fields(current_summary, new_summary_text)
                logger.debug(f"Merged result for {user_id}: {merged_summary[:500] if merged_summary else 'None'}...")
            else:
                # Clean and format new summary
                cleaned = self.parser.clean_text(new_summary_text)
                fields = self.parser.parse_to_dict(cleaned)
                merged_summary = self.parser.format_to_json(fields)
            
            # Save and reset tracking
            self.save_user_summary(user_id, merged_summary)
            self.reset_update_tracking(user_id)
            
            logger.info(f"Summary updated for {user_id}")
            return merged_summary
            
        except Exception as e:
            logger.error(f"Error updating summary for {user_id}: {e}")
            return None

    def _build_summary_prompt(self, current_summary: str, history: list) -> str:
        """
        Build the prompt for AI summary generation.
        
        Loads prompt template from file if available.
        """
        # Try to load prompt template
        template_content = self._load_prompt_template()
        
        # Format history for prompt
        history_text = self._format_history_for_prompt(history)
        
        if not template_content:
            raise FileNotFoundError("summary_prompt.json not found in prompts directory")
        
        # Use template
        prompt = template_content.replace("{current_summary}", current_summary or "Chưa có")
        prompt = prompt.replace("{history}", history_text)
        return prompt

    def _load_prompt_template(self) -> Optional[str]:
        """Load summary prompt template from file."""
        try:
            prompts_dir = Config.PROMPTS_DIR
            template_path = os.path.join(str(prompts_dir), 'summary_prompt.json')
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.debug(f"Could not load summary prompt template: {e}")
        
        return None

    def _format_history_for_prompt(self, history: list) -> str:
        """Format conversation history for inclusion in prompt."""
        if not history:
            return "Không có lịch sử hội thoại"
        
        lines = []
        for msg in history[-20:]:  # Last 20 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                lines.append(f"Người dùng: {content}")
            else:
                lines.append(f"Bot: {content}")
        
        return "\n".join(lines)

    # =========================================================================
    # Summary Format Validation
    # =========================================================================

    def validate_summary_format(self, summary: str) -> bool:
        """
        Validate that a summary is in the expected JSON format.
        
        Returns True if valid, False otherwise.
        """
        if not summary:
            return False
        
        try:
            data = json.loads(summary)
            
            # Check for required top-level sections
            required_sections = [
                'basic_info',
                'hobbies_and_passion',
                'personality_and_style',
            ]
            
            for section in required_sections:
                if section not in data:
                    logger.debug(f"Missing section: {section}")
                    return False
            
            return True
            
        except json.JSONDecodeError:
            logger.debug("Summary is not valid JSON")
            return False

    def get_summary_field(self, user_id: str, section: str, field: str) -> Optional[str]:
        """
        Get a specific field from user summary.
        
        Args:
            user_id: User identifier
            section: Top-level section (e.g., 'basic_info')
            field: Field within section (e.g., 'name')
        
        Returns:
            Field value or None if not found
        """
        summary = self.get_user_summary(user_id)
        if not summary:
            return None
        
        try:
            data = json.loads(summary)
            section_data = data.get(section, {})
            return section_data.get(field)
        except (json.JSONDecodeError, AttributeError):
            return None
