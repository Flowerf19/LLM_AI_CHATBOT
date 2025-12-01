import os
import logging
import json
from typing import Callable, Optional, List, Dict

logger = logging.getLogger(__name__)

class SummaryUpdateManager:
    def __init__(self, prompts_dir: Optional[str] = None, config_dir: Optional[str] = None, llm_service=None, summaries_dir: Optional[str] = None):
        # Chuẩn hóa: Luôn lưu vào src/data cho các file cấu hình và prompt
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # If explicit prompts_dir or config_dir provided, use it (for testing or custom deployment).
        if prompts_dir:
            self.prompts_dir = prompts_dir
        else:
            self.prompts_dir = os.path.join(project_root, 'data', 'prompts')
        if config_dir:
            self.config_dir = config_dir
        else:
            self.config_dir = os.path.join(project_root, 'data', 'config')
        self.llm_service = llm_service
        # Luôn xác định đường dẫn dựa trên vị trí file hiện tại
        if summaries_dir:
            # Use provided summaries_dir directly
            self.summaries_dir = summaries_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.summaries_dir = os.path.join(base_dir, 'data', 'user_summaries')
        self.important_keywords = self._load_important_keywords()
        self._last_update = {}
        # Cho phép gán các hàm thao tác file từ bên ngoài
        self.get_user_history: Optional[Callable[[str], List[Dict]]] = None
        self.get_user_summary: Optional[Callable[[str], str]] = None
        self.save_user_summary: Optional[Callable[[str, str], None]] = None

    def _clean_summary_text(self, text: str) -> str:
        import re
        if not text:
            return ""
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = text.replace('"', "")
        text = text.replace('\\n', '\n').replace('\\', '')
        text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def _parse_summary_fields(self, summary_text: str) -> dict:
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
            result[key] = m.group(1).strip() if m else None
        return result

    def _merge_summary_fields(self, old_summary: str, new_summary: str) -> str:
        old_clean = self._clean_summary_text(old_summary or "")
        new_clean = self._clean_summary_text(new_summary or "")
        old_fields = self._parse_summary_fields(old_clean)
        new_fields = self._parse_summary_fields(new_clean)
        merged = {}
        for k in old_fields:
            v_new = new_fields.get(k, None)
            # Nếu giá trị mới hợp lệ (không phải None, không trống, không phải 'Không có', khác giá trị cũ) thì lấy giá trị mới
            if v_new and v_new.strip() and v_new.lower() not in ["không có", "none"] and v_new != old_fields.get(k):
                merged[k] = v_new
            elif v_new and v_new.strip() and v_new.lower() not in ["không có", "none"]:
                merged[k] = v_new
            else:
                merged[k] = old_fields.get(k, "Không có")
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

    def _load_important_keywords(self) -> Dict:
        keywords_file = os.path.join(self.config_dir, 'important_keywords.json')
        default_keywords = {
            "basic_info": ["tên", "tuổi", "sinh", "sinh nhật", "ngày sinh"],
            "hobbies": ["thích", "yêu", "mê", "sở thích", "hobby"],
            "emotions": ["buồn", "vui", "stress", "lo", "hạnh phúc", "tâm trạng"],
            "relationships": ["độc thân", "người yêu", "bạn gái", "bạn trai"],
            "dreams": ["muốn", "ước", "dự định", "kế hoạch", "mơ ước"],
            "changes": ["không thích", "bỏ", "giờ thích", "chuyển sang", "chia tay", "có người yêu"]
        }
        if not os.path.exists(keywords_file):
            os.makedirs(os.path.dirname(keywords_file), exist_ok=True)
            try:
                with open(keywords_file, 'w', encoding='utf-8') as f:
                    json.dump(default_keywords, f, ensure_ascii=False, indent=2)
                logger.info(f"Created default keywords file: {keywords_file}")
            except Exception as e:
                logger.error(f"Error creating keywords file: {e}")
            return default_keywords
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading keywords file: {e}")
            return default_keywords

    def _is_template_summary(self, summary: str) -> bool:
        if not summary:
            return True
        template_indicators = [
            "[Không có]",
            "Tên: [Không có]",
            "Tuổi: [Không có]",
            "Sở thích: [Không có]"
        ]
        count = sum(1 for indicator in template_indicators if indicator in summary)
        if count >= 2:
            logger.info(f"🔍 Template summary detected ({count} indicators)")
            return True
        return False

    def should_update_summary(self, user_id: str, message_content: str, current_summary: str) -> bool:
        message_lower = message_content.lower()
        if self._is_template_summary(current_summary):
            logger.info(f"🔄 Template summary detected for {user_id} - FORCE UPDATE")
            return True
        for category, keywords in self.important_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    logger.info(f"Important keyword '{keyword}' found in message from {user_id}")
                    return True
        import random
        return random.random() < 0.3

    def _load_summary_prompt(self) -> str:
        prompt_file = os.path.join(self.prompts_dir, 'summary_prompt.json')
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    async def update_summary_smart(self, user_id: str, message_content: Optional[str] = None) -> Optional[str]:
        try:
            logger.info(f"🔄 Starting REALTIME summary update for user {user_id}")
            if not callable(self.get_user_history) or not callable(self.get_user_summary) or not callable(self.save_user_summary):
                raise Exception("SummaryUpdateManager: get_user_history, get_user_summary, save_user_summary must be set before calling update_summary_smart.")
            history = self.get_user_history(user_id)
            if history is None:
                history = []
            logger.info(f"📊 History stats for user {user_id}: {len(history)} total messages")
            if len(history) < 2:
                logger.info(f"📝 User {user_id}: Not enough messages ({len(history)}/2) for summary")
                self._last_update[user_id] = 0
                return None
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            unique_content = set(msg.get('content', '').strip().lower() for msg in user_messages)
            total_chars = sum(len(msg.get('content', '')) for msg in user_messages)
            existing_summary = self.get_user_summary(user_id)
            if existing_summary is None:
                existing_summary = ""
            is_template = self._is_template_summary(existing_summary)
            current_msg_count = len(history)
            last_update_count = self._last_update.get(user_id, 0)
            should_update = False
            if is_template:
                logger.info(f" TEMPLATE DETECTED for user {user_id}: Force updating...")
                should_update = True
            elif message_content and self.should_update_summary(user_id, message_content, existing_summary):
                logger.info(f" Important keyword or change detected for user {user_id}: Updating...")
                should_update = True
            elif current_msg_count - last_update_count >= 1:
                should_update = True
            if (len(unique_content) < 2 or total_chars < 15) and not (is_template or (message_content and self.should_update_summary(user_id, message_content, existing_summary))):
                logger.info(f" User {user_id}: Not enough diverse/long content for summary")
                self._last_update[user_id] = last_update_count
                return None
            if not should_update:
                logger.debug(f"📝 User {user_id}: No update needed (msg_count: {current_msg_count}, last: {last_update_count})")
                return existing_summary
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
            if self._is_template_summary(new_summary):
                logger.warning(f"⚠️ Generated summary is still template-like for user {user_id}")
                return existing_summary if not is_template else None
            self.save_user_summary(user_id, self._merge_summary_fields(existing_summary, new_summary.strip()))
            self._last_update[user_id] = len(history)
            logger.info(f"✅ REALTIME Summary updated for user {user_id} ({len(history)} total messages)")
            logger.info(f"📄 New summary preview: {new_summary.strip()[:100]}...")
            return new_summary.strip()
        except Exception as e:
            logger.error(f"❌ Error updating summary for {user_id}: {e}", exc_info=True)
            self._last_update[user_id] = 0
            return None 