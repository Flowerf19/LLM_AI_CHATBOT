"""
SummaryParser - Handles parsing, cleaning, and merging of user summary data.

Responsibility: Parse/transform summary text between different formats.
This is pure transformation logic with no I/O or business rules.
"""
import os
import json
import re
import logging
from typing import Dict, Optional
from config.settings import Config

logger = logging.getLogger(__name__)


class SummaryParser:
    """
    Handles parsing and transformation of user summary data.
    Supports both JSON and text-based summary formats.
    """
    
    # Field mappings for JSON <-> flat dict conversion
    FIELD_MAPPINGS = {
        # Basic Info
        "Tên": ("basic_info", "name"),
        "Tuổi": ("basic_info", "age"),
        "Sinh nhật": ("basic_info", "birthday"),
        # Hobbies
        "Công nghệ": ("hobbies_and_passion", "tech"),
        "Giải trí": ("hobbies_and_passion", "entertainment"),
        "Khác": ("hobbies_and_passion", "other"),
        # Personality
        "Giao tiếp": ("personality_and_style", "communication"),
        "Tâm trạng": ("personality_and_style", "mood"),
        "Đặc điểm": ("personality_and_style", "traits"),
        # Relationships
        "Bạn bè": ("relationships", "friends"),
        "Gia đình": ("relationships", "family"),
        "Đồng nghiệp": ("relationships", "colleagues"),
        "Người quan trọng": ("relationships", "significant_other"),
        "Ghi chú về tương tác": ("relationships", "interaction_notes"),
        # History
        "Chủ đề đã thảo luận": ("interaction_history", "discussed_topics"),
        "Mức độ thân thiết": ("interaction_history", "intimacy_level"),
        "Ghi chú đặc biệt": ("interaction_history", "special_notes"),
        # Projects
        "Hiện tại": ("projects_and_goals", "current"),
        "Kế hoạch": ("projects_and_goals", "plans"),
    }
    
    # Regex patterns for text-based parsing
    TEXT_FIELD_PATTERNS = [
        ("Tên", r"Tên:\s*(.*)"),
        ("Tuổi", r"Tuổi:\s*(.*)"),
        ("Sinh nhật", r"Sinh nhật:\s*(.*)"),
        ("Công nghệ", r"Công nghệ:\s*(.*)"),
        ("Giải trí", r"Giải trí:\s*(.*)"),
        ("Khác", r"Khác:\s*(.*)"),
        ("Giao tiếp", r"Giao tiếp:\s*(.*)"),
        ("Tâm trạng", r"Tâm trạng:\s*(.*)"),
        ("Đặc điểm", r"Đặc điểm:\s*(.*)"),
        ("Bạn bè", r"Bạn bè:\s*(.*)"),
        ("Gia đình", r"Gia đình:\s*(.*)"),
        ("Đồng nghiệp", r"Đồng nghiệp:\s*(.*)"),
        ("Người quan trọng", r"Người quan trọng:\s*(.*)"),
        ("Ghi chú về tương tác", r"Ghi chú về tương tác:\s*(.*)"),
        ("Chủ đề đã thảo luận", r"Chủ đề đã thảo luận:\s*(.*)"),
        ("Mức độ thân thiết", r"Mức độ thân thiết:\s*(.*)"),
        ("Ghi chú đặc biệt", r"Ghi chú đặc biệt:\s*(.*)"),
        ("Hiện tại", r"Hiện tại:\s*(.*)"),
        ("Kế hoạch", r"Kế hoạch:\s*(.*)"),
    ]

    def clean_text(self, text: str) -> str:
        """
        Remove escape sequences, markdown, and extra characters from summary text.
        Preserves valid JSON content.
        """
        if not text:
            return ""
        
        # If the text is valid JSON, return as-is
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        
        # Remove code block markdown
        text = re.sub(r"```[\s\S]*?```", "", text)
        # Remove extra quotes (not for JSON)
        text = text.replace('"', "")
        # Remove escape sequences
        text = text.replace('\\n', '\n').replace('\\', '')
        # Remove JSON-like syntax if not valid JSON
        text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        # Normalize whitespace
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        
        return text

    def parse_to_dict(self, summary_text: str) -> Dict[str, Optional[str]]:
        """
        Parse summary text (JSON or text format) into a flat dictionary.
        Returns dict with Vietnamese field names as keys.
        """
        # Try JSON parsing first
        try:
            data = json.loads(summary_text)
            if isinstance(data, dict):
                return self._parse_json_to_flat(data)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fall back to text-based parsing
        return self._parse_text_to_flat(summary_text)

    def _parse_json_to_flat(self, data: dict) -> Dict[str, Optional[str]]:
        """Convert nested JSON structure to flat dict with Vietnamese keys."""
        flat_data = {}
        
        for viet_key, (section, field) in self.FIELD_MAPPINGS.items():
            section_data = data.get(section, {})
            if isinstance(section_data, dict):
                value = section_data.get(field)
                flat_data[viet_key] = str(value) if value is not None else None
            else:
                flat_data[viet_key] = None
        
        return flat_data

    def _parse_text_to_flat(self, text: str) -> Dict[str, Optional[str]]:
        """Parse text format summary using regex patterns."""
        result = {}
        
        for key, pattern in self.TEXT_FIELD_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result[key] = match.group(1).strip()
            else:
                result[key] = None
        
        return result

    def merge_fields(self, old_summary: str, new_summary: str) -> str:
        """
        Merge old and new summary data.
        Only updates fields with new non-empty values.
        Preserves old values when new values are empty or 'Không có'.
        """
        # Clean and parse both summaries
        old_clean = self.clean_text(old_summary or "")
        new_clean = self.clean_text(new_summary or "")
        
        old_fields = self.parse_to_dict(old_clean)
        new_fields = self.parse_to_dict(new_clean)
        
        # Merge: prefer new values unless empty or 'Không có'
        merged = {}
        for key in old_fields:
            new_value = new_fields.get(key)
            if new_value and new_value.lower() != "không có":
                merged[key] = new_value
            else:
                merged[key] = old_fields.get(key, "Không có")
        
        # Format to output
        return self.format_to_json(merged)

    def format_to_json(self, flat_data: Dict[str, Optional[str]]) -> str:
        """
        Format flat dictionary to JSON output.
        Uses template file if available, otherwise creates simple JSON.
        """
        try:
            prompts_dir = getattr(Config, 'PROMPTS_DIR', 'src/data/prompts')
            if isinstance(prompts_dir, str):
                format_path = os.path.join(prompts_dir, 'summary_format.json')
            else:
                format_path = prompts_dir / 'summary_format.json'
            
            if os.path.exists(format_path):
                with open(format_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                filled_data = self._fill_template(template_data, flat_data)
                return json.dumps(filled_data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error loading summary template: {e}")
        
        # Fallback: simple JSON dump
        return json.dumps(flat_data, ensure_ascii=False, indent=2)

    def _fill_template(self, data, values: dict):
        """Recursively fill template placeholders with values."""
        if isinstance(data, dict):
            return {k: self._fill_template(v, values) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._fill_template(item, values) for item in data]
        elif isinstance(data, str):
            # Check if string is a placeholder like "{Key}"
            if data.startswith("{") and data.endswith("}"):
                key = data[1:-1]
                val = values.get(key)
                return val if val is not None else "Không có"
            return data
        else:
            return data

    def is_template_summary(self, summary: str) -> bool:
        """
        Check if summary is a template (has '[Không có]' placeholder entries).
        Returns True if summary appears to be unfilled template.
        """
        if not summary:
            return True
        
        # Check for template indicators in the raw string
        template_indicators = [
            "[Không có]",
            "Chưa xác định",
            "Không rõ",
        ]
        
        # Count total occurrences of all template indicators
        count = sum(summary.count(indicator) for indicator in template_indicators)
        
        if count >= 2:
            logger.debug(f"Template summary detected ({count} indicators)")
            return True
        
        return False
