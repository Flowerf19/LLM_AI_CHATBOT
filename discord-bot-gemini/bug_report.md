# Bug Report

**Bot:** Bé Bảy#2174 | **Date:** February 3, 2026

---

## ✅ Bug #1: Command Duplicate Responses - FIXED

**Status:** RESOLVED  
**Priority:** MEDIUM

**Issue:** Commands (!ping, !status, !relationships) phản hồi 2 lần

**Root Cause:** 

- File: `src/services/messeger/llm_message_service.py:44`
- Gọi `await self.bot.process_commands(message)` thủ công trong khi discord.py đã tự động xử lý commands

**Fix:**
```python
# ❌ BEFORE
await self.bot.process_commands(message)  # Gây duplicate
return

# ✅ AFTER  
return  # Bỏ dòng gọi thủ công
```

---

## 🔴 Bug #2: Summary Extraction Failed - OPEN

**Status:** OPEN  
**Priority:** MEDIUM

**Issue:** User summary không extract thông tin từ conversation history. Tất cả fields = "Không có"

**Example:**

- Input: "t tên Hòa, 25 tuổi, thích học Python và AI"
- Expected: name="Hòa", age="25 tuổi", tech="Python, AI"
- Actual: name="Không có", age="Không có", tech="Không có"

**Location:**

- `src/services/user_summary/summary_service.py` - `_generate_summary()`
- `src/data/prompts/summary_prompt.json`

**Possible Causes:**

- Prompt construction issue
- AI model limitation (qwen3:4b-instruct)
- Data format mismatch

**TODO:**

- [ ] Log prompt sent to AI
- [ ] Test with Gemini model
- [ ] Review prompt template
- [ ] Check SummaryParser

---

**Stats:** 2 bugs | 1 fixed | 1 open
