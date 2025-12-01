import os
import logging
from typing import Dict, List, Optional
import json
import re
from discord.ext import commands
from config.settings import Config

logger = logging.getLogger(__name__)


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

        if not text:
            return ""
        # If the text is valid JSON, return as-is (don't strip JSON content)
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        # Xoá code block markdown
        text = re.sub(r"```[\s\S]*?```", "", text)
        # Xoá dấu ngoặc kép thừa (không áp dụng cho JSON vì chúng đã được trả về phía trên)
        text = text.replace('"', "")
        # Xoá các ký tự escape \n, \\n+        text = text.replace('\\n', '\n').replace('\\', '')
        # Nếu không phải JSON, xoá các đoạn ngoặc nhọn/cú pháp giống JSON (nếu có)
        text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        # Xoá khoảng trắng thừa
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text
    def _parse_summary_fields(self, summary_text: str) -> dict:
        """Parse summary text thành dict các trường chính (theo format chuẩn)."""
        import re
        import json
        
        # Try parsing as JSON first (for new format)
        try:
            data = json.loads(summary_text)
            flat_data = {}
            
            # Map JSON structure back to internal keys
            if isinstance(data, dict):
                # Basic Info
                basic = data.get("basic_info", {})
                flat_data["Tên"] = basic.get("name")
                flat_data["Tuổi"] = basic.get("age")
                flat_data["Sinh nhật"] = basic.get("birthday")
                
                # Hobbies
                hobbies = data.get("hobbies_and_passion", {})
                flat_data["Công nghệ"] = hobbies.get("tech")
                flat_data["Giải trí"] = hobbies.get("entertainment")
                flat_data["Khác"] = hobbies.get("other")
                
                # Personality
                personality = data.get("personality_and_style", {})
                flat_data["Giao tiếp"] = personality.get("communication")
                flat_data["Tâm trạng"] = personality.get("mood")
                flat_data["Đặc điểm"] = personality.get("traits")
                
                # Relationships
                rels = data.get("relationships", {})
                flat_data["Bạn bè"] = rels.get("friends")
                flat_data["Gia đình"] = rels.get("family")
                flat_data["Đồng nghiệp"] = rels.get("colleagues")
                flat_data["Người quan trọng"] = rels.get("significant_other")
                flat_data["Ghi chú về tương tác"] = rels.get("interaction_notes")
                
                # History
                history = data.get("interaction_history", {})
                flat_data["Chủ đề đã thảo luận"] = history.get("discussed_topics")
                flat_data["Mức độ thân thiết"] = history.get("intimacy_level")
                flat_data["Ghi chú đặc biệt"] = history.get("special_notes")
                
                # Projects
                projects = data.get("projects_and_goals", {})
                flat_data["Hiện tại"] = projects.get("current")
                flat_data["Kế hoạch"] = projects.get("plans")
                
                # Return only non-None values
                return {k: str(v) if v is not None else None for k, v in flat_data.items()}
        except (json.JSONDecodeError, AttributeError):
            pass

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
            import json
            # Ensure path is correct and handle potential Path/str mismatch
            prompts_dir = getattr(Config, 'PROMPTS_DIR', 'src/data/prompts')
            if isinstance(prompts_dir, str):
                format_path = os.path.join(prompts_dir, 'summary_format.json')
            else:
                format_path = prompts_dir / 'summary_format.json'
                
            with open(format_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Recursive function to fill template
            def fill_template(data, values):
                if isinstance(data, dict):
                    return {k: fill_template(v, values) for k, v in data.items()}
                elif isinstance(data, list):
                    return [fill_template(item, values) for item in data]
                elif isinstance(data, str):
                    # Check if string is a placeholder like "{Key}"
                    if data.startswith("{") and data.endswith("}"):
                        key = data[1:-1]
                        # Handle None values gracefully
                        val = values.get(key)
                        return val if val is not None else "Không có"
                    return data
                else:
                    return data

            filled_data = fill_template(template_data, merged)
            return json.dumps(filled_data, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error loading or formatting summary template: {e}", exc_info=True)
            # Fallback to simple JSON dump of merged data to avoid reverting to text format
            return json.dumps(merged, ensure_ascii=False, indent=2)
    def __init__(self, llm_service, prompts_dir: str = None, config_dir: str = None):
        self.llm_service = llm_service
        
        self.prompts_dir = Config.PROMPTS_DIR
        self.config_dir = Config.DATA_DIR / 'config'
        self.summaries_dir = Config.USER_SUMMARIES_DIR
        
        logger.info(f"📁 SummaryService using directory: {self.summaries_dir}")
        
        # Ensure directories exist
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load important keywords
        self.important_keywords = self._load_important_keywords()
        
        # Tracking for updates
        self._last_update = {}
    
    def _load_important_keywords(self) -> Dict:
        """Load important keywords for summary updates"""
        import json
        config_path = os.path.join(self.config_dir, 'important_keywords.json')
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Loaded important_keywords from: {config_path}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading important_keywords from {config_path}: {e}")
                
        logger.warning("No important_keywords.json found. Summary updates will rely on random chance.")
        return {}
    
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
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.json")
        
        content = ""
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Error loading JSON summary for {user_id}: {e}")
        
        if content and len(content) > 10:
            logger.debug(f"📖 Loaded summary for {user_id}: {len(content)} chars")
            return content
        else:
            logger.debug(f"📝 Empty summary for {user_id}")
            return ""
    
    def save_user_summary(self, user_id: str, summary: str):
        """Save user summary với absolute path"""
        import json
        summary_file = os.path.join(self.summaries_dir, f"{user_id}_summary.json")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            
            # Nếu summary là string, thử parse json
            data = summary
            if isinstance(summary, str):
                try:
                    data = json.loads(summary)
                except Exception:
                    # Nếu không phải json, giữ nguyên string (cho legacy text format)
                    # Nhưng tốt nhất là convert sang dict nếu có thể
                    pass

            with open(summary_file, 'w', encoding='utf-8') as f:
                if isinstance(data, dict) or isinstance(data, list):
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    # Fallback for raw text
                    f.write(str(data))
                    
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
                    logger.info("📝 LLM returned JSON, converting to text format for summary.")
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
        prompt_file = os.path.join(self.prompts_dir, 'summary_prompt.json')
        
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