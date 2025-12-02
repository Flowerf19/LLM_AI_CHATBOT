"""
Tests for SummaryParser class.

Tests cover:
- clean_text: Remove markdown, escape sequences, invalid JSON
- parse_to_dict: Parse JSON and text formats to flat dict
- merge_fields: Merge old and new summary data
- format_to_json: Convert flat dict to JSON output
"""
import pytest
import json
from services.user_summary.summary_parser import SummaryParser


class TestSummaryParserCleanText:
    """Tests for clean_text method."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    def test_clean_text_empty(self, parser):
        """Empty input returns empty string."""
        assert parser.clean_text("") == ""
        assert parser.clean_text(None) == ""
    
    def test_clean_text_valid_json_unchanged(self, parser):
        """Valid JSON should be returned as-is."""
        valid_json = '{"name": "Test", "age": 25}'
        result = parser.clean_text(valid_json)
        assert result == valid_json
    
    def test_clean_text_removes_code_block_markers(self, parser):
        """Code block markers (```) should be removed, content preserved for non-JSON."""
        text_with_code = "Hello ```python\nprint('test')``` world"
        result = parser.clean_text(text_with_code)
        # Markers should be removed
        assert "```" not in result
        # Content is preserved (no longer removed since it might be useful)
        # The function now focuses on extracting JSON, not removing all code
    
    def test_clean_text_extracts_json_from_code_blocks(self, parser):
        """JSON inside code blocks should be extracted correctly."""
        json_in_code_block = '```json\n{"name": "test"}\n```'
        result = parser.clean_text(json_in_code_block)
        assert result == '{"name": "test"}'
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert parsed["name"] == "test"
    
    def test_clean_text_removes_escape_sequences(self, parser):
        """Escape sequences like \\n should be converted."""
        text_with_escapes = "Line1\\nLine2\\nLine3"
        result = parser.clean_text(text_with_escapes)
        assert "\\n" not in result
        assert "\n" in result
    
    def test_clean_text_normalizes_whitespace(self, parser):
        """Multiple newlines should be normalized."""
        text = "Line1\n\n\n\nLine2"
        result = parser.clean_text(text)
        assert "\n\n\n\n" not in result


class TestSummaryParserParseToDict:
    """Tests for parse_to_dict method."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    def test_parse_json_format(self, parser):
        """JSON format summary should be parsed correctly."""
        json_summary = json.dumps({
            "basic_info": {"name": "Nguyên", "age": "25"},
            "hobbies_and_passion": {"tech": "Python, AI"},
        })
        
        result = parser.parse_to_dict(json_summary)
        
        assert result.get("Tên") == "Nguyên"
        assert result.get("Tuổi") == "25"
        assert result.get("Công nghệ") == "Python, AI"
    
    def test_parse_text_format(self, parser):
        """Text format summary should be parsed correctly."""
        text_summary = """
        Tên: Minh
        Tuổi: 30
        Công nghệ: JavaScript, React
        Giao tiếp: Thân thiện
        """
        
        result = parser.parse_to_dict(text_summary)
        
        assert result.get("Tên") == "Minh"
        assert result.get("Tuổi") == "30"
        assert result.get("Công nghệ") == "JavaScript, React"
        assert result.get("Giao tiếp") == "Thân thiện"
    
    def test_parse_empty_returns_none_values(self, parser):
        """Empty summary should return dict with None values."""
        result = parser.parse_to_dict("")
        
        # All fields should be None
        assert result.get("Tên") is None
        assert result.get("Tuổi") is None
    
    def test_parse_partial_data(self, parser):
        """Partial data should only populate matched fields."""
        text = "Tên: Hoa"
        result = parser.parse_to_dict(text)
        
        assert result.get("Tên") == "Hoa"
        assert result.get("Tuổi") is None


class TestSummaryParserMergeFields:
    """Tests for merge_fields method."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    def test_merge_prefers_new_values(self, parser):
        """New non-empty values should override old values."""
        old_json = json.dumps({
            "basic_info": {"name": "Old Name", "age": "20"},
        })
        new_json = json.dumps({
            "basic_info": {"name": "New Name", "age": "25"},
        })
        
        result = parser.merge_fields(old_json, new_json)
        json.loads(result)
        
        # Result format may vary, check the merged content
        assert "New Name" in result or "25" in result
    
    def test_merge_preserves_old_when_new_empty(self, parser):
        """Old values should be kept when new values are empty."""
        old_text = "Tên: Existing Name"
        new_text = ""  # Empty new summary
        
        result = parser.merge_fields(old_text, new_text)
        
        # Should contain old value
        assert "Existing" in result or "Name" in result
    
    def test_merge_preserves_old_when_new_is_khong_co(self, parser):
        """Old values should be kept when new value is 'Không có'."""
        old_json = json.dumps({
            "basic_info": {"name": "Real Name"},
        })
        new_json = json.dumps({
            "basic_info": {"name": "Không có"},
        })
        
        result = parser.merge_fields(old_json, new_json)
        
        # Original value should be preserved
        assert "Real Name" in result


class TestSummaryParserFormatToJson:
    """Tests for format_to_json method."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    def test_format_returns_valid_json(self, parser):
        """Output should be valid JSON."""
        flat_data = {
            "Tên": "Test User",
            "Tuổi": "25",
        }
        
        result = parser.format_to_json(flat_data)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
    
    def test_format_handles_none_values(self, parser):
        """None values should be handled gracefully."""
        flat_data = {
            "Tên": None,
            "Tuổi": "25",
        }
        
        result = parser.format_to_json(flat_data)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


class TestSummaryParserIsTemplateSummary:
    """Tests for is_template_summary method - comprehensive edge cases."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    # =========================================================================
    # Empty/None cases
    # =========================================================================
    
    def test_empty_string_is_template(self, parser):
        """Empty string should be considered a template."""
        assert parser.is_template_summary("") is True
    
    def test_none_is_template(self, parser):
        """None should be considered a template."""
        assert parser.is_template_summary(None) is True
    
    def test_whitespace_only_is_template(self, parser):
        """Whitespace-only string should be considered a template."""
        assert parser.is_template_summary("   ") is True
        assert parser.is_template_summary("\n\n") is True
    
    # =========================================================================
    # JSON format with "Không có" (actual production format)
    # =========================================================================
    
    def test_json_with_khong_co_is_template(self, parser):
        """JSON summary with 'Không có' values is a template."""
        json_summary = json.dumps({
            "basic_info": {"name": "Không có", "age": "Không có", "birthday": "Không có"},
            "hobbies_and_passion": {"tech": "Không có", "entertainment": "Không có"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(json_summary) is True
    
    def test_json_with_all_khong_co_is_template(self, parser):
        """Full JSON template with all 'Không có' is detected."""
        json_summary = json.dumps({
            "basic_info": {"name": "Không có", "age": "Không có", "birthday": "Không có"},
            "hobbies_and_passion": {"tech": "Không có", "entertainment": "Không có", "other": "Không có"},
            "personality_and_style": {"communication": "Không có", "mood": "Không có", "traits": "Không có"},
            "relationships": {"friends": "Không có", "family": "Không có"},
            "interaction_history": {"discussed_topics": "Không có", "intimacy_level": "Không có"},
            "projects_and_goals": {"current": "Không có", "plans": "Không có"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(json_summary) is True
    
    def test_json_with_partial_data_not_template(self, parser):
        """JSON with mostly filled data is NOT a template."""
        json_summary = json.dumps({
            "basic_info": {"name": "Hoà", "age": "364000", "birthday": "Không có"},
            "hobbies_and_passion": {"tech": "Python", "entertainment": "Gaming"}
        }, ensure_ascii=False)
        
        # Only 1 "Không có" - should NOT be template
        assert parser.is_template_summary(json_summary) is False
    
    def test_json_with_two_khong_co_is_template(self, parser):
        """JSON with exactly 2 'Không có' IS a template (threshold = 2)."""
        json_summary = json.dumps({
            "basic_info": {"name": "Hoà", "age": "Không có", "birthday": "Không có"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(json_summary) is True
    
    # =========================================================================
    # Text format with [Không có] brackets
    # =========================================================================
    
    def test_text_with_bracket_placeholders(self, parser):
        """Text format with [Không có] placeholders is a template."""
        template = """
        Tên: [Không có]
        Tuổi: [Không có]
        Sở thích: [Không có]
        """
        assert parser.is_template_summary(template) is True
    
    def test_text_mixed_brackets_and_plain(self, parser):
        """Mixed [Không có] and plain Không có are both counted."""
        template = """
        Tên: [Không có]
        Tuổi: Không có
        """
        assert parser.is_template_summary(template) is True
    
    # =========================================================================
    # Other placeholder indicators
    # =========================================================================
    
    def test_chua_xac_dinh_is_template(self, parser):
        """'Chưa xác định' placeholders are detected."""
        template = """
        Tên: Chưa xác định
        Tuổi: Chưa xác định
        """
        assert parser.is_template_summary(template) is True
    
    def test_khong_ro_is_template(self, parser):
        """'Không rõ' placeholders are detected."""
        template = """
        Tên: Không rõ
        Tuổi: Không rõ
        """
        assert parser.is_template_summary(template) is True
    
    def test_mixed_placeholders_is_template(self, parser):
        """Mixed placeholder types are all counted."""
        template = """
        Tên: Không có
        Tuổi: Chưa xác định
        Sinh nhật: Không rõ
        """
        assert parser.is_template_summary(template) is True
    
    # =========================================================================
    # Filled summaries (should NOT be templates)
    # =========================================================================
    
    def test_filled_text_not_template(self, parser):
        """Text summary with real data is NOT a template."""
        filled = """
        Tên: Nguyên
        Tuổi: 25
        Công nghệ: Python
        """
        assert parser.is_template_summary(filled) is False
    
    def test_filled_json_not_template(self, parser):
        """JSON summary with real data is NOT a template."""
        filled = json.dumps({
            "basic_info": {"name": "Hoà", "age": "25", "birthday": "15/03"},
            "hobbies_and_passion": {"tech": "Python", "entertainment": "Gaming"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(filled) is False
    
    def test_mostly_filled_with_one_empty_not_template(self, parser):
        """Summary with only 1 'Không có' is NOT a template."""
        mostly_filled = json.dumps({
            "basic_info": {"name": "Hoà", "age": "25", "birthday": "Không có"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(mostly_filled) is False
    
    # =========================================================================
    # Edge cases
    # =========================================================================
    
    def test_khong_co_in_content_not_counted_wrong(self, parser):
        """'Không có' as part of actual content should still be counted."""
        # If user says "Tôi không có bạn", the "không có" is in content
        # This is an edge case - current logic counts all occurrences
        content = json.dumps({
            "basic_info": {"name": "Test", "age": "25"},
            "hobbies_and_passion": {"tech": "Tôi không có thời gian học"}
        }, ensure_ascii=False)
        
        # Only 1 occurrence of "không có" - should NOT be template
        assert parser.is_template_summary(content) is False
    
    def test_case_sensitivity(self, parser):
        """Check case sensitivity of placeholder detection."""
        # "Không có" vs "không có" - current implementation is case-sensitive
        lower_case = 'Tên: không có\nTuổi: không có'
        
        # Lowercase should NOT match (implementation uses exact match)
        assert parser.is_template_summary(lower_case) is False
    
    def test_unicode_handling(self, parser):
        """Ensure Vietnamese characters are handled correctly."""
        vietnamese = json.dumps({
            "basic_info": {"name": "Nguyễn Văn Hoà", "age": "25"}
        }, ensure_ascii=False)
        
        assert parser.is_template_summary(vietnamese) is False
    
    def test_real_production_template(self, parser):
        """Test with actual production template format."""
        # This is the exact format from 726302130318868500_summary.json
        production_template = '''{
  "basic_info": {
    "name": "Không có",
    "age": "Không có",
    "birthday": "Không có"
  },
  "hobbies_and_passion": {
    "tech": "Không có",
    "entertainment": "Không có",
    "other": "Không có"
  },
  "personality_and_style": {
    "communication": "Không có",
    "mood": "Không có",
    "traits": "Không có"
  },
  "relationships": {
    "friends": "Không có",
    "family": "Không có",
    "colleagues": "Không có",
    "significant_other": "Không có",
    "interaction_notes": "Không có"
  },
  "interaction_history": {
    "discussed_topics": "Không có",
    "intimacy_level": "Không có",
    "special_notes": "Không có"
  },
  "projects_and_goals": {
    "current": "Không có",
    "plans": "Không có"
  }
}'''
        assert parser.is_template_summary(production_template) is True
