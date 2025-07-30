import discord
import os
import aiofiles
import asyncio
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

from discord.ext import commands
# Extension setup function for discord.py
async def setup(bot: commands.Bot):
    # Thêm Cog thực thi vào bot
    await bot.add_cog(SummaryServiceCog(bot))
    logger.info("✅ SummaryServiceCog loaded and extension setup called")

# Định nghĩa Cog cho bot
class SummaryServiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Có thể khởi tạo các service phụ ở đây nếu cần

    # Đảm bảo không có hàm on_message listener ở đây để tránh duplicate responses

    # XÓA LỆNH PING NẾU CÓ

class SummaryService:
    def _clean_summary_text(self, text: str) -> str:
        """Loại bỏ escape, markdown, ký tự thừa khỏi summary text."""
        import re
        if not text:
            return ""
        # Xoá code block markdown
        text = re.sub(r"```[\s\S]*?```", "", text)
        # Xoá dấu ngoặc kép thừa
        text = text.replace('"', "")
        # Xoá các ký tự escape \n, \\n+        text = text.replace('\\n', '\n').replace('\\', '')
        # Xoá các đoạn JSON hoặc dấu ngoặc thừa
        text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        # Xoá khoảng trắng thừa
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text
    def _parse_summary_fields(self, summary_text: str) -> dict:
        """Parse summary text thành dict các trường chính (theo format chuẩn)."""
        import re
        fields = [
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
            ("Kế hoạch", r"Kế hoạch:\s*(.*)")
        ]
        result = {}
        for key, pattern in fields:
            m = re.search(pattern, summary_text)
            if m:
                result[key] = m.group(1).strip()
            else:
                result[key] = None
        return result

    def _merge_summary_fields(self, old_summary: str, new_summary: str) -> str:
        """Chỉ cập nhật trường có thông tin mới, giữ lại trường cũ nếu trường mới rỗng hoặc 'Không có'."""
        import re
        import os
        # Làm sạch text trước khi parse
        old_clean = self._clean_summary_text(old_summary or "")
        new_clean = self._clean_summary_text(new_summary or "")
        old_fields = self._parse_summary_fields(old_clean)
        new_fields = self._parse_summary_fields(new_clean)
        # Nếu trường mới rỗng hoặc 'Không có' thì giữ trường cũ
        merged = {}
        for k in old_fields:
            v_new = new_fields.get(k, None)
            if v_new and v_new.lower() != "không có":
                merged[k] = v_new
            else:
                merged[k] = old_fields.get(k, "Không có")
        # Load template format từ file
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(os.path.dirname(base_dir))
            format_path = os.path.join(src_dir, 'data', 'prompts', 'summary_format.txt')
            with open(format_path, 'r', encoding='utf-8') as f:
                template = f.read()
            # Format template với merged dict
            return template.format(**merged)
        except Exception as e:
            logger.error(f"Error loading or formatting summary template: {e}")
            # Fallback về format cứng nếu lỗi
            lines = []
            lines.append("=== THÔNG TIN CƠ BẢN ===")
            lines.append(f"Tên: {merged['Tên']}")
            lines.append(f"Tuổi: {merged['Tuổi']}")
            lines.append(f"Sinh nhật: {merged['Sinh nhật']}")
            lines.append("=== SỞ THÍCH & ĐAM MÊ ===")
            lines.append(f"• Công nghệ: {merged['Công nghệ']}")
            lines.append(f"• Giải trí: {merged['Giải trí']}")
            lines.append(f"• Khác: {merged['Khác']}")
            lines.append("=== TÍNH CÁCH & PHONG CÁCH ===")
            lines.append(f"• Giao tiếp: {merged['Giao tiếp']}")
            lines.append(f"• Tâm trạng: {merged['Tâm trạng']}")
            lines.append(f"• Đặc điểm: {merged['Đặc điểm']}")
            lines.append("=== MỐI QUAN HỆ VỚI NGƯỜI KHÁC ===")
            lines.append(f"• Bạn bè: {merged['Bạn bè']}")
            lines.append(f"• Gia đình: {merged['Gia đình']}")
            lines.append(f"• Đồng nghiệp: {merged['Đồng nghiệp']}")
            lines.append(f"• Người quan trọng: {merged['Người quan trọng']}")
            lines.append(f"• Ghi chú về tương tác: {merged['Ghi chú về tương tác']}")
            lines.append("=== LỊCH SỬ TƯƠNG TÁC ===")
            lines.append(f"• Chủ đề đã thảo luận: {merged['Chủ đề đã thảo luận']}")
            lines.append(f"• Mức độ thân thiết: {merged['Mức độ thân thiết']}")
            lines.append(f"• Ghi chú đặc biệt: {merged['Ghi chú đặc biệt']}")
            lines.append("=== DỰ ÁN & MỤC TIÊU ===")
            lines.append(f"• Hiện tại: {merged['Hiện tại']}")
            lines.append(f"• Kế hoạch: {merged['Kế hoạch']}")
            return "\n".join(lines)
    def __init__(self, llm_service, prompts_dir: str, config_dir: str):
        self.llm_service = llm_service
        # Đảm bảo lưu đúng vào src/data/user_summaries
        base_dir = os.path.dirname(os.path.abspath(__file__))  # .../src/services/...
        src_dir = os.path.dirname(os.path.dirname(base_dir))    # .../src
        self.prompts_dir = os.path.join(src_dir, 'data', 'prompts')
        self.config_dir = os.path.join(src_dir, 'data', 'config')
        self.summaries_dir = os.path.join(src_dir, 'data', 'user_summaries')
        
        logger.info(f"📁 SummaryService using directory: {self.summaries_dir}")
        
        # Ensure directories exist
        os.makedirs(self.summaries_dir, exist_ok=True)
        os.makedirs(self.prompts_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load important keywords
        self.important_keywords = self._load_important_keywords()
        
        # Tracking for updates
        self._last_update = {}
    
    def _load_important_keywords(self) -> Dict:
        """Load important keywords for summary updates"""
        import json
        # Ưu tiên file dummy nếu có
        dummy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dummy', 'important_keywords.json')
        config_path = os.path.join(self.config_dir, 'important_keywords.json')
        default_keywords = {
            "basic_info": ["tên", "tuổi", "sinh", "sinh nhật", "ngày sinh"],
            "hobbies": ["thích", "yêu", "mê", "sở thích", "hobby"],
            "emotions": ["buồn", "vui", "stress", "lo", "hạnh phúc", "tâm trạng"],
            "relationships": ["độc thân", "người yêu", "bạn gái", "bạn trai"],
            "dreams": ["muốn", "ước", "dự định", "kế hoạch", "mơ ước"],
            "changes": ["không thích", "bỏ", "giờ thích", "chuyển sang", "chia tay", "có người yêu"]
        }
        for path in [dummy_path, config_path]:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        logger.info(f"Loaded important_keywords from: {path}")
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading important_keywords from {path}: {e}")
        logger.warning("No important_keywords.json found, using default keywords.")
        return default_keywords
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """FIXED: Get user conversation history với absolute path"""
        history_file = os.path.join(self.summaries_dir, f"{user_id}_history.json")
        
        logger.debug(f"🔍 Looking for history file: {history_file}")
        logger.debug(f"🔍 SummaryService summaries_dir: {self.summaries_dir}")
        logger.debug(f"🔍 File exists: {os.path.exists(history_file)}")
        
        # Check if file exists with absolute path
        if not os.path.exists(history_file):
            logger.info(f"📝 History file not found: {history_file}")
            return []
        
        try:
            # Check file size first
            file_size = os.path.getsize(history_file)
            logger.debug(f"📄 History file size: {file_size} bytes")
            
            if file_size == 0:
                logger.warning(f"📝 History file is empty: {history_file}")
                return []
            
            with open(history_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.debug(f"📄 Raw file content length: {len(content)} chars")
                
                if not content.strip():
                    logger.warning(f"📝 History file has no content: {history_file}")
                    return []
                
                # Parse JSON
                history = json.loads(content)
                
                if not isinstance(history, list):
                    logger.error(f"📝 History file format invalid (not a list): {history_file}")
                    return []
                
                logger.info(f"✅ Successfully loaded {len(history)} messages for user {user_id}")
                return history
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error for {user_id}: {e}")
            logger.error(f"❌ File content preview: {content[:200] if 'content' in locals() else 'N/A'}")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading history for {user_id}: {e}")
            return []
    
    def get_user_summary(self, user_id: str) -> str:
        """Get user summary với absolute path và better caching"""
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        
        if not os.path.exists(summary_file):
            logger.debug(f"📝 Summary file not found: {summary_file}")
            return ""
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if content and len(content) > 10:
                logger.debug(f"📖 Loaded summary for {user_id}: {len(content)} chars")
                return content
            else:
                logger.debug(f"📝 Empty summary for {user_id}")
                return ""
                
        except Exception as e:
            logger.error(f"Error loading summary for {user_id}: {e}")
            return ""
    
    def save_user_summary(self, user_id: str, summary: str):
        """Save user summary với absolute path"""
        import json
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            # Nếu summary là dict, chuyển thành text
            if isinstance(summary, dict):
                summary = json.dumps(summary, ensure_ascii=False, indent=2)
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary.strip())
            logger.info(f"📝 Summary saved for user {user_id} at: {summary_file}")
        except Exception as e:
            logger.error(f"Error saving summary for {user_id}: {e}")
    
    def should_update_summary(self, user_id: str, message_content: str, current_summary: str) -> bool:
        """REALTIME: Enhanced check for immediate summary updates"""
        message_lower = message_content.lower()
        
        # FORCE UPDATE cho template summary
        if self._is_template_summary(current_summary):
            logger.info(f"🔄 Template summary detected for {user_id} - FORCE UPDATE")
            return True
        
        # Check for important keywords
        for category, keywords in self.important_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    logger.info(f"Important keyword '{keyword}' found in message from {user_id}")
                    return True
        
        # REALTIME: Tăng tần suất update
        import random
        return random.random() < 0.3  # Tăng từ 10% lên 30%

    def _is_template_summary(self, summary: str) -> bool:
        """Check if summary is a template (has [Không có] entries)"""
        if not summary:
            return True
        
        template_indicators = [
            "[Không có]",
            "Tên: [Không có]",
            "Tuổi: [Không có]",
            "Sở thích: [Không có]"
        ]
        
        # Nếu có >= 2 template indicators → là template
        count = sum(1 for indicator in template_indicators if indicator in summary)
        
        if count >= 2:
            logger.info(f"🔍 Template summary detected ({count} indicators)")
            return True
        
        return False

    async def update_summary_smart(self, user_id: str, message_content: Optional[str] = None) -> Optional[str]:
        """REALTIME: Force update để đảm bảo summary được cập nhật ngay, tối ưu logic cập nhật."""
        import json
        try:
            logger.info(f"🔄 Starting REALTIME summary update for user {user_id}")
            history = self.get_user_history(user_id)
            logger.info(f"📊 History stats for user {user_id}: {len(history)} total messages")
            if len(history) < 1:
                logger.info(f"📝 User {user_id}: Not enough messages ({len(history)}/1) for summary")
                self._last_update[user_id] = 0
                return None
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            unique_content = set(msg.get('content', '').strip().lower() for msg in user_messages)
            total_chars = sum(len(msg.get('content', '')) for msg in user_messages)
            existing_summary = self.get_user_summary(user_id)
            is_template = self._is_template_summary(existing_summary)
            current_msg_count = len(history)
            last_update_count = self._last_update.get(user_id, 0)
            # Ưu tiên update nếu là template hoặc có từ khóa quan trọng hoặc có tin nhắn mới
            should_update = False
            if is_template:
                logger.info(f"🔄 TEMPLATE DETECTED for user {user_id}: Force updating...")
                should_update = True
            elif message_content and self.should_update_summary(user_id, message_content, existing_summary):
                logger.info(f"🔄 Important keyword or change detected for user {user_id}: Updating...")
                should_update = True
            elif current_msg_count - last_update_count >= 1:
                should_update = True
            # Nếu không đủ đa dạng hoặc quá ngắn, chỉ cho update nếu là template hoặc có từ khóa quan trọng
            if (len(unique_content) < 1 or total_chars < 10) and not (is_template or (message_content and self.should_update_summary(user_id, message_content, existing_summary))):
                logger.info(f"📝 User {user_id}: Not enough diverse/long content for summary")
                self._last_update[user_id] = last_update_count
                return None
            if not should_update:
                logger.debug(f"📝 User {user_id}: No update needed (msg_count: {current_msg_count}, last: {last_update_count})")
                return existing_summary
            # Chuẩn bị dữ liệu hội thoại
            recent_history = history[-20:]
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history if msg.get('content')
            ])
            logger.info(f"📝 User {user_id}: Generating summary from {len(recent_history)} recent messages")
            summary_prompt_template = self._load_summary_prompt()
            summary_prompt = f"""{summary_prompt_template}

QUAN TRỌNG: Tạo summary hoàn toàn mới dựa trên cuộc hội thoại thực tế.
KHÔNG sử dụng "[Không có]" - chỉ ghi thông tin có thật.

Cuộc hội thoại cần phân tích:
{conversation_text}

Hãy tạo tóm tắt chi tiết và chính xác:"""
            logger.info(f"🤖 Sending REALTIME summary request to LLM for user {user_id}")
            new_summary = await self.llm_service.generate_response(summary_prompt, user_id)
            if not new_summary or len(new_summary.strip()) < 15:
                logger.warning(f"⚠️ Generated summary too short for user {user_id}: '{new_summary}'")
                return existing_summary if not is_template else None
            # Nếu LLM trả về JSON, tự động chuyển sang text format chuẩn
            try:
                parsed = json.loads(new_summary)
                if isinstance(parsed, dict):
                    logger.info(f"📝 LLM returned JSON, converting to text format for summary.")
                    # Chuyển dict sang text format chuẩn bằng _merge_summary_fields
                    new_summary = self._merge_summary_fields(existing_summary, json.dumps(parsed, ensure_ascii=False))
            except Exception:
                pass  # Không phải JSON, giữ nguyên
            if self._is_template_summary(new_summary):
                logger.warning(f"⚠️ Generated summary is still template-like for user {user_id}")
                return existing_summary if not is_template else None
            merged_summary = self._merge_summary_fields(existing_summary, new_summary.strip())
            self.save_user_summary(user_id, merged_summary)
            self._last_update[user_id] = len(history)
            logger.info(f"✅ REALTIME Summary updated for user {user_id} ({len(history)} total messages)")
            logger.info(f"📄 New summary preview: {merged_summary[:100]}...")
            return merged_summary
        except Exception as e:
            logger.error(f"❌ Error updating summary for {user_id}: {e}", exc_info=True)
            self._last_update[user_id] = 0
            return None
    
    def _load_summary_prompt(self) -> str:
        """Load summary prompt from file"""
        prompt_file = os.path.join(self.prompts_dir, 'summary_prompt.txt')
        
        if not os.path.exists(prompt_file):
            return "Phân tích cuộc hội thoại và tạo tóm tắt thông tin người dùng."
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading summary prompt: {e}")
            return "Phân tích cuộc hội thoại và tạo tóm tắt thông tin người dùng."
    
    def clear_user_summary(self, user_id: str):
        """Clear user summary"""
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.txt")
        
        if os.path.exists(summary_file):
            try:
                os.remove(summary_file)
                logger.info(f"Summary cleared for user {user_id}")
            except Exception as e:
                logger.error(f"Error clearing summary for {user_id}: {e}")