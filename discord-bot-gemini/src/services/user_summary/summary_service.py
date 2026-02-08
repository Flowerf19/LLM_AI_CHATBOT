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
from discord import Client

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
    HISTORY_THRESHOLD_RATIO = 0.8  # 80% of max history triggers update
    MAX_PERSISTENT_HISTORY = 100  # Max messages in persistent history

    def __init__(self, bot: Optional[Client] = None):
        self.bot = bot
        self.data_manager = SummaryDataManager()
        self.parser = SummaryParser()

        # Track last update per user
        self._last_update_time: dict[str, float] = {}

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

    def reset_update_tracking(self, user_id: str):
        """Reset tracking after a successful update."""
        self._last_update_time[user_id] = time.time()

    def is_context_nearly_full(self, user_id: str) -> bool:
        """
        Check if user's conversation history is nearly full (80% threshold).
        Triggers summary update to preserve information before history is truncated.
        """
        history = self.get_user_history(user_id)
        if not history:
            return False

        history_count = len(history)
        threshold = int(self.MAX_PERSISTENT_HISTORY * self.HISTORY_THRESHOLD_RATIO)

        if history_count >= threshold:
            logger.debug(
                f"📊 History nearly full for {user_id}: {history_count}/{self.MAX_PERSISTENT_HISTORY}"
            )
            return True

        return False

    # =========================================================================
    # AI-Powered Summary Generation
    # =========================================================================

    async def update_summary_smart(
        self,
        user_id: str,
        ai_service,
        recent_messages: list = None,
        force: bool = False,
    ) -> Optional[str]:
        """
        Generate or update user summary using AI.

        Args:
            user_id: User identifier
            ai_service: AI service (Gemini/DeepSeek) for generation
            recent_messages: Recent conversation messages
            force: Force update (unused, kept for API compatibility)

        Returns:
            New summary string if updated, None otherwise
        """

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
            if hasattr(ai_service, "generate_summary"):
                new_summary_text = await ai_service.generate_summary(prompt)
            else:
                result = await ai_service.generate_response(prompt)
                # Handle tuple return (text, is_important) from generate_response
                new_summary_text = result[0] if isinstance(result, tuple) else result

            logger.debug(
                f"AI response for {user_id}: {new_summary_text[:500] if new_summary_text else 'None'}..."
            )

            if not new_summary_text or new_summary_text.startswith("Error"):
                logger.warning(
                    f"AI returned empty or error summary for {user_id}: {new_summary_text}"
                )
                return None

            # Merge with existing summary (preserves old data)
            if current_summary:
                logger.debug(f"Merging summary for {user_id}")
                merged_summary = self.parser.merge_fields(
                    current_summary, new_summary_text
                )
                logger.debug(
                    f"Merged result for {user_id}: {merged_summary[:500] if merged_summary else 'None'}..."
                )
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
            raise FileNotFoundError(
                "summary_prompt.json not found in prompts directory"
            )

        # Use template
        prompt = template_content.replace(
            "{current_summary}", current_summary or "Chưa có"
        )
        prompt = prompt.replace("{history}", history_text)
        return prompt

    def _load_prompt_template(self) -> Optional[str]:
        """Load summary prompt template from file."""
        try:
            prompts_dir = Config.PROMPTS_DIR
            template_path = os.path.join(str(prompts_dir), "summary_prompt.json")

            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
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
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
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
                "basic_info",
                "hobbies_and_passion",
                "personality_and_style",
            ]

            for section in required_sections:
                if section not in data:
                    logger.debug(f"Missing section: {section}")
                    return False

            return True

        except json.JSONDecodeError:
            logger.debug("Summary is not valid JSON")
            return False

    def get_summary_field(
        self, user_id: str, section: str, field: str
    ) -> Optional[str]:
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
