# 📁 Project Structure: Discord Bot Gemini

Dưới đây là mô tả cấu trúc thư mục và các thành phần chính của project:

```
discord-bot-gemini/
├── src/
│   ├── bot.py                # Main entry point for the Discord bot
│   ├── config/               # Cấu hình bot, logging, settings
│   ├── data/                 # Dữ liệu bot (prompts, user summaries, relationships, ...)
│   ├── models/               # Định nghĩa các data model (User, Channel, Conversation, ...)
│   ├── services/             # Business logic, chia theo domain (ai, channel, conversation, ...)
│   │   ├── ai/               # Service liên quan AI, LLM, Gemini, summary
│   │   ├── channel/          # Service quản lý kênh, channel config
│   │   ├── conversation/     # Service quản lý hội thoại, anti-spam, message processing
│   │   ├── relationship/     # Service về mối quan hệ, phân tích tương tác
│   │   ├── user/             # Service về lệnh người dùng
│   │   ├── base_service.py   # Base class cho các service
│   │   └── __init__.py
│   ├── utils/                # Hàm helper, tiện ích dùng chung
│   └── __init__.py
├── requirements.txt          # Danh sách package Python cần cài
├── README.md                 # Hướng dẫn sử dụng tổng quan
├── PROJECT_STRUCTURE.md      # (File này) Mô tả cấu trúc project
├── *.md                      # Các file hướng dẫn, technical docs, guide cho từng tính năng
```

## Ý nghĩa các thư mục/file chính
- **src/bot.py**: Điểm khởi động bot, load các service, cấu hình event.
- **src/config/**: Cấu hình bot, logging, settings, lấy biến môi trường.
- **src/data/**: Lưu trữ dữ liệu bot (prompts, lịch sử, mối quan hệ, ...).
- **src/models/**: Định nghĩa các model dữ liệu (User, Channel, Conversation, ...).
- **src/services/**: Chứa toàn bộ business logic, chia nhỏ theo domain (AI, channel, hội thoại, ...).
- **src/utils/**: Hàm tiện ích dùng chung cho toàn project.
- **requirements.txt**: Danh sách package Python cần thiết.
- **README.md**: Hướng dẫn sử dụng, cài đặt, chạy bot.
- **PROJECT_STRUCTURE.md**: Mô tả cấu trúc project, giải thích ý nghĩa các thành phần.
- **Các file *.md khác**: Hướng dẫn chi tiết từng tính năng, technical docs, guide cho user/dev.

---

> **Lưu ý:**
> - Mọi thay đổi lớn về cấu trúc nên cập nhật lại file này để các thành viên khác dễ nắm bắt.
> - Nếu thêm module mới, hãy bổ sung mô tả vào đây. 