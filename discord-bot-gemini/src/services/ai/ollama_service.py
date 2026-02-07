import aiohttp
import asyncio
import logging
from typing import Optional, List
from config.settings import Config


class OllamaService:
    """
    Ollama service for local LLM inference.
    Uses Qwen 1.7B model via Ollama API.
    """

    def __init__(self):
        self.api_url: str = Config.OLLAMA_API_URL
        self.model: str = Config.OLLAMA_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("discord_bot.OllamaService")

        # Load prompts (same as Gemini)
        self.personality_prompt: str = self._load_prompt("personality.json")
        self.conversation_prompt: str = self._load_prompt("conversation_prompt.json")

        self.logger.info(f"🦙 Ollama service initialized with model: {self.model}")

    def _load_prompt(self, filename: str) -> str:
        filepath = Config.PROMPTS_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                self.logger.info(f"✅ Loaded prompt: {filename}")
                return content
        else:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_response(
        self, prompt: str, user_id: Optional[str] = None, conversation_context: str = ""
    ) -> str:
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
                "num_predict": 1000,  # Max tokens
                "num_ctx": 8192,  # Tăng context window để đọc được lịch sử hội thoại
            },
        }

        try:
            self.logger.debug(
                f"Sending request to Ollama API with prompt: {full_prompt[:100]}..."
            )

            async with session.post(
                api_endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(
                        f"Ollama API error ({response.status}): {error_text}"
                    )
                    return "Error: Ollama API không phản hồi. Kiểm tra xem Ollama có đang chạy không (ollama serve)."

                response_data = await response.json()

                # Extract response text from Ollama format
                if "response" in response_data:
                    generated_text = response_data["response"].strip()
                    if generated_text:
                        # Clean response: remove prompt markers and Unicode emoji
                        generated_text = self._clean_response(generated_text)
                        self.logger.debug(
                            f"✅ Ollama response: {generated_text[:50]}..."
                        )
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

    def _build_full_prompt(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_context: str = "",
    ) -> str:
        """Build complete prompt with personality, conversation guidelines, and context"""
        prompt_parts: List[str] = []

        # Add personality
        if self.personality_prompt:
            prompt_parts.append(f"=== NHÂN CÁCH ===\n{self.personality_prompt}")

        # Add conversation guidelines
        if self.conversation_prompt:
            prompt_parts.append(
                f"=== HƯỚNG DẪN HỘI THOẠI ===\n{self.conversation_prompt}"
            )

        # Add conversation context if available
        if conversation_context:
            prompt_parts.append(f"=== BỐI CẢNH HỘI THOẠI ===\n{conversation_context}")

        # Add user message
        prompt_parts.append(f"=== TIN NHẮN CỦA NGƯỜI DÙNG ===\n{user_message}")

        # Add instruction
        prompt_parts.append("\n=== PHẢN HỒI CỦA BẠN ===")

        return "\n\n".join(prompt_parts)

    async def generate_summary(self, prompt: str) -> str:
        """Generate user summary using Ollama"""
        return await self.generate_response(prompt)

    def _clean_response(self, text: str) -> str:
        """
        Clean response by removing:
        - Prompt markers (=== ... ===)
        - Unicode emoji (chỉ giữ text emoticons)
        """
        import re

        # Remove prompt section markers
        markers = [
            r"===\s*PHẢN HỒI CỦA BẠN\s*===",
            r"===\s*TIN NHẮN CỦA NGƯỜI DÙNG\s*===",
            r"===\s*NHÂN CÁCH\s*===",
            r"===\s*HƯỚNG DẪN HỘI THOẠI\s*===",
            r"===\s*BỐI CẢNH HỘI THOẠI\s*===",
            r"===\s*[^=]+\s*===",  # Generic marker pattern
        ]
        for marker in markers:
            text = re.sub(marker, "", text, flags=re.IGNORECASE)

        # Remove Unicode emoji (keep ASCII emoticons like :) :v :3)
        # This regex matches most emoji in Unicode ranges
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map
            "\U0001f1e0-\U0001f1ff"  # flags
            "\U00002702-\U000027b0"  # dingbats
            "\U0001f900-\U0001f9ff"  # supplemental symbols
            "\U0001fa00-\U0001fa6f"  # chess symbols
            "\U0001fa70-\U0001faff"  # symbols and pictographs extended
            "\U00002600-\U000026ff"  # misc symbols
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub("", text)

        # Clean up extra whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text.strip()

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("🔒 Ollama session closed")
