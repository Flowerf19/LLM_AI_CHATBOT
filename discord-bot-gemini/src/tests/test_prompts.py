"""
Tests for prompt file loading.

Tests cover:
- Loading JSON prompt files from PROMPTS_DIR
- Validating prompt file structure
- GeminiService prompt initialization
"""
import pytest
import json
from pathlib import Path


class TestPromptFiles:
    """Test suite for prompt JSON files."""
    
    @pytest.fixture
    def prompts_dir(self):
        """Get prompts directory path."""
        # Navigate from tests/ to data/prompts/
        current_dir = Path(__file__).parent
        return current_dir.parent / 'data' / 'prompts'
    
    def test_prompts_dir_exists(self, prompts_dir):
        """Prompts directory should exist."""
        assert prompts_dir.exists(), f"Prompts dir not found: {prompts_dir}"
    
    def test_all_prompt_files_exist(self, prompts_dir):
        """All required prompt files should exist."""
        required_files = [
            'conversation_prompt.json',
            'personality.json',
            'server_relationships_prompt.json',
            'summary_format.json',
            'summary_prompt.json',
            'task_instruction.json',
        ]
        
        for filename in required_files:
            filepath = prompts_dir / filename
            assert filepath.exists(), f"Missing prompt file: {filename}"
    
    def test_all_prompt_files_valid_json(self, prompts_dir):
        """All prompt files should be valid JSON."""
        json_files = list(prompts_dir.glob('*.json'))
        assert len(json_files) >= 6, "Expected at least 6 prompt files"
        
        for filepath in json_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    assert isinstance(data, dict), f"{filepath.name} should be a dict"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {filepath.name}: {e}")


class TestConversationPrompt:
    """Tests for conversation_prompt.json structure."""
    
    @pytest.fixture
    def prompt_data(self):
        """Load conversation_prompt.json."""
        current_dir = Path(__file__).parent
        filepath = current_dir.parent / 'data' / 'prompts' / 'conversation_prompt.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_has_description(self, prompt_data):
        """Should have description field."""
        assert 'description' in prompt_data
    
    def test_has_rules(self, prompt_data):
        """Should have rules section."""
        assert 'rules' in prompt_data
        assert 'general' in prompt_data['rules']
        assert 'conversation_flow' in prompt_data['rules']
    
    def test_has_relationship_handling(self, prompt_data):
        """Should have relationship handling section."""
        assert 'relationship_handling' in prompt_data
        assert 'usage' in prompt_data['relationship_handling']
        assert 'tracking' in prompt_data['relationship_handling']
    
    def test_has_information_processing(self, prompt_data):
        """Should have information processing rules."""
        assert 'information_processing' in prompt_data
        assert 'critical_rules' in prompt_data['information_processing']
        assert 'naming' in prompt_data['information_processing']
    
    def test_has_important_warnings(self, prompt_data):
        """Should have important warnings list."""
        assert 'important_warnings' in prompt_data
        assert isinstance(prompt_data['important_warnings'], list)
        assert len(prompt_data['important_warnings']) >= 5


class TestPersonalityPrompt:
    """Tests for personality.json structure."""
    
    @pytest.fixture
    def prompt_data(self):
        """Load personality.json."""
        current_dir = Path(__file__).parent
        filepath = current_dir.parent / 'data' / 'prompts' / 'personality.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_has_character_info(self, prompt_data):
        """Should have character and game fields."""
        assert 'character' in prompt_data
        assert prompt_data['character'] == 'March 7th'
        assert 'game' in prompt_data
    
    def test_has_personality_traits(self, prompt_data):
        """Should have personality traits."""
        assert 'personality' in prompt_data
        assert isinstance(prompt_data['personality'], list)
        assert len(prompt_data['personality']) >= 3
    
    def test_has_hobbies(self, prompt_data):
        """Should have hobbies list."""
        assert 'hobbies' in prompt_data
        assert isinstance(prompt_data['hobbies'], list)
    
    def test_has_quote(self, prompt_data):
        """Should have a quote."""
        assert 'quote' in prompt_data
        assert len(prompt_data['quote']) > 10


class TestSummaryFormatPrompt:
    """Tests for summary_format.json structure."""
    
    @pytest.fixture
    def prompt_data(self):
        """Load summary_format.json."""
        current_dir = Path(__file__).parent
        filepath = current_dir.parent / 'data' / 'prompts' / 'summary_format.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_has_required_sections(self, prompt_data):
        """Should have all required top-level sections."""
        required_sections = [
            'basic_info',
            'hobbies_and_passion',
            'personality_and_style',
            'relationships',
            'interaction_history',
            'projects_and_goals',
        ]
        
        for section in required_sections:
            assert section in prompt_data, f"Missing section: {section}"
    
    def test_basic_info_fields(self, prompt_data):
        """basic_info should have name, age, birthday."""
        basic_info = prompt_data['basic_info']
        assert 'name' in basic_info
        assert 'age' in basic_info
        assert 'birthday' in basic_info
    
    def test_relationships_fields(self, prompt_data):
        """relationships should have required fields."""
        relationships = prompt_data['relationships']
        assert 'friends' in relationships
        assert 'family' in relationships
        assert 'significant_other' in relationships


class TestSummaryPrompt:
    """Tests for summary_prompt.json structure."""
    
    @pytest.fixture
    def prompt_data(self):
        """Load summary_prompt.json."""
        current_dir = Path(__file__).parent
        filepath = current_dir.parent / 'data' / 'prompts' / 'summary_prompt.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_has_instructions(self, prompt_data):
        """Should have instructions list."""
        assert 'instructions' in prompt_data
        assert isinstance(prompt_data['instructions'], list)
        assert len(prompt_data['instructions']) >= 5
    
    def test_has_placeholders(self, prompt_data):
        """Should have placeholders for template substitution."""
        assert 'placeholders' in prompt_data
        placeholders = prompt_data['placeholders']
        assert 'current_summary' in placeholders
        assert 'history' in placeholders
    
    def test_has_output_format(self, prompt_data):
        """Should define expected output format."""
        assert 'output_format' in prompt_data
        output_format = prompt_data['output_format']
        assert 'basic_info' in output_format
        assert 'relationships' in output_format


class TestTaskInstructionPrompt:
    """Tests for task_instruction.json structure."""
    
    @pytest.fixture
    def prompt_data(self):
        """Load task_instruction.json."""
        current_dir = Path(__file__).parent
        filepath = current_dir.parent / 'data' / 'prompts' / 'task_instruction.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_has_role(self, prompt_data):
        """Should define AI role."""
        assert 'role' in prompt_data
    
    def test_has_instructions(self, prompt_data):
        """Should have instructions list."""
        assert 'instructions' in prompt_data
        assert isinstance(prompt_data['instructions'], list)
        assert len(prompt_data['instructions']) >= 3
    
    def test_has_task_placeholder(self, prompt_data):
        """Should have task placeholder."""
        assert 'placeholder' in prompt_data
        assert 'task' in prompt_data['placeholder']
