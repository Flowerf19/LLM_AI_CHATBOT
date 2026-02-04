import aiohttp
import asyncio
import logging
from typing import Optional, List
from src.config.settings import Config

class OllamaService:
    """
    Ollama service for local LLM inference.
    Uses Qwen 1.7B model via Ollama API.
    """
    
    def __init__(self):
        self.api_url: str = Config.OLLAMA_API_URL
        self.model: str = Config.OLLAMA_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger('discord_bot.OllamaService')
        
        # Load prompts (same as Gemini)
        self.personality_prompt: str = self._load_prompt('personality.json')
        self.conversation_prompt: str = self._load_prompt('conversation_prompt.json')
        
        self.logger.info(f"🦙 Ollama service initialized with model: {self.model}")
        
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
        """
        Generate response using Ollama API.
        
        Args:
            prompt: User message
            user_id: User identifier
            conversation_context: Previous conversation context
            
        Returns:
            Generated response text
        """
        session = await self._get_session()
        
        # Build full prompt with personality, conversation guidelines, and context
        full_prompt = self._build_full_prompt(prompt, user_id, conversation_context)
        
        # Ollama API endpoint
        api_endpoint = f"{self.api_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,  # No streaming for simpler implementation
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 1000  # Max tokens
            }
        }

        try:
            self.logger.debug(f"Sending request to Ollama API with prompt: {full_prompt[:100]}...")
            
            async with session.post(api_endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Ollama API error ({response.status}): {error_text}")
                    return "Error: Ollama API không phản hồi. Kiểm tra xem Ollama có đang chạy không (ollama serve)."
                
                response_data = await response.json()
                
                # Extract response text from Ollama format
                if 'response' in response_data:
                    generated_text = response_data['response'].strip()
                    if generated_text:
                        self.logger.debug(f"✅ Ollama response: {generated_text[:50]}...")
                        return generated_text
                    else:
                        self.logger.warning("Empty response from Ollama")
                        return "Xin lỗi, tôi không thể tạo phản hồi."
                
                self.logger.error(f"Unexpected Ollama response format: {response_data}")
                return "Error: Unexpected response format from Ollama."
                
        except aiohttp.ClientConnectorError as e:
            self.logger.error(f"Cannot connect to Ollama: {e}")
            return "Error: Không thể kết nối đến Ollama. Đảm bảo Ollama đang chạy (ollama serve)."
        except asyncio.TimeoutError:
            self.logger.error("Ollama API timeout")
            return "Error: Ollama response timeout (>60s)."
        except Exception as e:
            self.logger.error(f"Error communicating with Ollama API: {e}")
            return f"Error: {str(e)}"
    
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
            prompt_parts.append(f"=== BỐI CẢNH HỘI THOẠI ===\n{conversation_context}")
        
        # Add user message
        prompt_parts.append(f"=== TIN NHẮN CỦA NGƯỜI DÙNG ===\n{user_message}")
        
        # Add instruction
        prompt_parts.append("\n=== PHẢN HỒI CỦA BẠN ===")
        
        return "\n\n".join(prompt_parts)

    async def generate(self, prompt: str) -> str:
        """Generate response for batch processing (alias for generate_response)"""
        return await self.generate_response(prompt)
    
    async def generate_summary(self, prompt: str) -> str:
        """Generate user summary using Ollama"""
        return await self.generate_response(prompt)

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("🔒 Ollama session closed")
