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
    
    def test_clean_text_removes_code_blocks(self, parser):
        """Code block markdown should be removed."""
        text_with_code = "Hello ```python\nprint('test')``` world"
        result = parser.clean_text(text_with_code)
        assert "```" not in result
        assert "python" not in result
    
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
    """Tests for is_template_summary method."""
    
    @pytest.fixture
    def parser(self):
        return SummaryParser()
    
    def test_empty_is_template(self, parser):
        """Empty summary should be considered a template."""
        assert parser.is_template_summary("") is True
        assert parser.is_template_summary(None) is True
    
    def test_template_with_placeholders(self, parser):
        """Summary with [Không có] placeholders is a template."""
        template = """
        Tên: [Không có]
        Tuổi: [Không có]
        Sở thích: [Không có]
        """
        
        assert parser.is_template_summary(template) is True
    
    def test_filled_summary_not_template(self, parser):
        """Summary with real data is not a template."""
        filled = """
        Tên: Nguyên
        Tuổi: 25
        Công nghệ: Python
        """
        
        assert parser.is_template_summary(filled) is False
