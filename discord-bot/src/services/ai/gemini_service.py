import os
import aiohttp
import logging
from typing import Optional, List
from src.config.settings import Config

class GeminiService:
    def __init__(self):
        self.api_key: Optional[str] = Config.GEMINI_API_KEY
        self.api_url: str = Config.GEMINI_API_URL
        self.model: str = Config.LLM_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger('discord_bot.GeminiService')
        
        # Load prompts
        self.personality_prompt: str = self._load_prompt('personality.json')
        self.conversation_prompt: str = self._load_prompt('conversation_prompt.json')
        
    def _load_prompt(self, filename: str) -> str:
        filepath = Config.PROMPTS_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self.logger.info(f"✅ Loaded prompt: {filename}")
                return content
        else:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_response(self, prompt: str, user_id: Optional[str] = None, conversation_context: str = "") -> str:
        if not self.api_key:
            self.logger.error("Gemini API key not found")
            return "Error: API key not configured."

        session = await self._get_session()
        
        # Build full prompt with personality, conversation guidelines, and context
        full_prompt = self._build_full_prompt(prompt, user_id, conversation_context)
        
        # Construct the full API URL for generateContent
        full_url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
                "topP": 0.95,
                "topK": 64
            }
        }

        try:
            self.logger.debug(f"Sending request to Gemini API with full prompt: {full_prompt[:100]}...")
            async with session.post(full_url, json=payload, headers={
                'Content-Type': 'application/json'
            }) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Gemini API error: {error_text}")
                    return "Error generating response."
                
                response_data = await response.json()
                
                # Extract the text from the response
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            return parts[0]['text']
                
                self.logger.error(f"Unexpected response format: {response_data}")
                return "Error: Unexpected response format."
                
        except Exception as e:
            self.logger.error(f"Error communicating with Gemini API: {e}")
            return "Error generating response."
    
    def _build_full_prompt(self, user_message: str, user_id: Optional[str] = None, conversation_context: str = "") -> str:
        """Build complete prompt with personality, conversation guidelines, and context"""
        prompt_parts: List[str] = []
        
        # Add personality
        if self.personality_prompt:
            prompt_parts.append(f"=== NHÂN CÁCH ===\n{self.personality_prompt}")
        
        # Add conversation guidelines
        if self.conversation_prompt:
            prompt_parts.append(f"=== HƯỚNG DẪN HỘI THOẠI ===\n{self.conversation_prompt}")
        
        # Add conversation context if available
        if conversation_context:
            prompt_parts.append(f"=== LỊCH SỬ HỘI THOẠI GẦN ĐÂY ===\n{conversation_context}")
        
        # Add user message
        prompt_parts.append(f"=== TIN NHẮN NGƯỜI DÙNG ===\n{user_message}")
        
        # Add instructions from file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(os.path.dirname(current_dir))
        prompts_dir = os.path.join(src_dir, 'data', 'prompts')
        task_file = os.path.join(prompts_dir, 'task_instruction.json')
        if os.path.exists(task_file):
            with open(task_file, 'r', encoding='utf-8') as f:
                task_instruction = f.read().strip()
        else:
            raise FileNotFoundError(f"Task instruction prompt file not found: {task_file}")
        prompt_parts.append(task_instruction)
        
        full_prompt = "\n\n".join(prompt_parts)
        self.logger.debug(f"Built full prompt with context: {len(full_prompt)} chars")
        return full_prompt

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def generate_summary(self, prompt: str) -> str:
        """
        Generate a summary using the AI API without personality/conversation prompts.
        This is used for user summary generation, not chat responses.
        """
        if not self.api_key:
            self.logger.error("Gemini API key not found")
            return "Error: API key not configured."

        session = await self._get_session()
        
        # Construct the full API URL for generateContent
        full_url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.5,  # Lower for more consistent output
                "maxOutputTokens": 2000,  # Higher for detailed summaries
                "topP": 0.9,
                "topK": 40
            }
        }

        try:
            self.logger.debug(f"Generating summary with prompt: {prompt[:100]}...")
            async with session.post(full_url, json=payload, headers={
                'Content-Type': 'application/json'
            }) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Gemini API error for summary: {error_text}")
                    return "Error generating summary."
                
                response_data = await response.json()
                
                # Extract the text from the response
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            self.logger.info("✅ Summary generated successfully")
                            return parts[0]['text']
                
                self.logger.error(f"Unexpected response format for summary: {response_data}")
                return "Error: Unexpected response format."
                
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Error generating summary."

    def split_response_into_parts(self, response: str) -> List[str]:
        """Split response into multiple natural parts for sequential sending"""
        import re
        
        # Remove extra whitespace
        response = response.strip()
        
        # Split by natural breaks (sentences, questions, exclamations)
        parts = re.split(r'([.!?]+\s*)', response)
        
        # Combine sentence with its punctuation
        combined_parts: List[str] = []
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                part = (parts[i] + parts[i + 1]).strip()
            else:
                part = parts[i].strip()
            
            if part:
                combined_parts.append(part)
        
        # If no natural splits found, split by length
        if len(combined_parts) <= 1 and len(response) > 100:
            # Split by commas or natural pauses
            parts = re.split(r'([,;]\s*)', response)
            combined_parts = []
            current_part = ""
            
            for part in parts:
                if len(current_part + part) < 80:
                    current_part += part
                else:
                    if current_part.strip():
                        combined_parts.append(current_part.strip())
                    current_part = part
            
            if current_part.strip():
                combined_parts.append(current_part.strip())
        
        # Ensure no part is too long (max 200 chars)
        final_parts: List[str] = []
        for part in combined_parts:
            if len(part) > 200:
                # Split long parts by words
                words = part.split()
                current_chunk = ""
                
                for word in words:
                    if len(current_chunk + " " + word) < 200:
                        current_chunk += (" " + word) if current_chunk else word
                    else:
                        if current_chunk:
                            final_parts.append(current_chunk.strip())
                        current_chunk = word
                
                if current_chunk:
                    final_parts.append(current_chunk.strip())
            else:
                final_parts.append(part)
        
        # Ensure we have at least one part
        if not final_parts:
            final_parts = [response]
        
        self.logger.debug(f"Split response into {len(final_parts)} parts")
        return final_parts

    async def generate(self, prompt: str) -> str:
        """Generate response for batch processing (alias for generate_response)"""
        return await self.generate_response(prompt)