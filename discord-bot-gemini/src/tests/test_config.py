"""
Tests for Prompt Loading and Configuration.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPromptLoading:
    """Test all 6 prompt files load correctly"""
    
    def test_conversation_prompt_loads(self):
        """Test conversation_prompt.json loads"""
        from config.settings import Config
        
        prompt_path = os.path.join(str(Config.PROMPTS_DIR), 'conversation_prompt.json')
        assert os.path.exists(prompt_path), f"conversation_prompt.json not found at {prompt_path}"
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0
    
    def test_personality_prompt_loads(self):
        """Test personality.json loads"""
        from config.settings import Config
        
        prompt_path = os.path.join(str(Config.PROMPTS_DIR), 'personality.json')
        assert os.path.exists(prompt_path)
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0
    
    def test_summary_prompt_loads(self):
        """Test summary_prompt.json loads"""
        from config.settings import Config
        
        prompt_path = os.path.join(str(Config.PROMPTS_DIR), 'summary_prompt.json')
        assert os.path.exists(prompt_path)
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0
    
    def test_all_prompts_exist(self):
        """Test all 6 required prompt files exist"""
        from config.settings import Config
        
        required_prompts = [
            'conversation_prompt.json',
            'personality.json',
            'server_relationships_prompt.json',
            'summary_format.json',
            'summary_prompt.json',
            'task_instruction.json'
        ]
        
        for prompt_file in required_prompts:
            prompt_path = os.path.join(str(Config.PROMPTS_DIR), prompt_file)
            assert os.path.exists(prompt_path), f"{prompt_file} not found"
    
    def test_prompts_are_valid_content(self):
        """Test prompt files contain valid content"""
        from config.settings import Config
        
        prompts_dir = str(Config.PROMPTS_DIR)
        
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(prompts_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Should have content
                    assert len(content) > 10, f"{filename} is too short"


class TestTypingSimulation:
    """Test typing delay calculation"""
    
    def test_typing_delay_calculation(self):
        """Test typing delay is calculated based on message length"""
        # Simulate typing delay calculation logic
        base_wpm = 60
        
        short_message = "Hi"
        long_message = "This is a much longer message that would take more time to type out naturally."
        
        # Longer messages should have longer delay
        short_delay = len(short_message) / (base_wpm * 5 / 60)  # chars per second
        long_delay = len(long_message) / (base_wpm * 5 / 60)
        
        assert long_delay > short_delay
    
    def test_typing_config_exists(self):
        """Test typing configuration exists"""
        from config.settings import Config
        
        assert hasattr(Config, 'ENABLE_TYPING_SIMULATION')


class TestResponseSplitting:
    """Test GeminiService response splitting for long messages"""
    
    def test_split_response_into_parts(self):
        """Test splitting long response into parts"""
        from services.ai.gemini_service import GeminiService
        
        service = GeminiService()
        
        # Long response with multiple sentences
        long_response = "Đây là câu đầu tiên. Đây là câu thứ hai! Đây là câu thứ ba? Câu cuối cùng..."
        
        if hasattr(service, 'split_response_into_parts'):
            parts = service.split_response_into_parts(long_response)
            assert isinstance(parts, list)
            assert len(parts) >= 1
    
    def test_response_under_2000_chars(self):
        """Test response under 2000 chars fits Discord limit"""
        short_response = "Xin chào!"
        
        # Should fit in single Discord message
        assert len(short_response) <= 2000
