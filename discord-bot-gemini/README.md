# Discord Bot - Gemini API

This project is a Discord bot that utilizes the Gemini API for various functionalities. The bot is designed to interact with users in Discord servers, providing responses based on user input and leveraging the capabilities of the Gemini API.

## Project Structure

```
discord-bot-gemini
├── src
│   ├── bot.py                # Main entry point for the Discord bot
│   ├── cogs                  # Directory containing individual cogs for bot functionalities
│   ├── config                # Configuration files for logging and settings
│   ├── data                  # Data files including prompts and user summaries
│   ├── models                # Data models for managing bot data
│   ├── services              # Service files for business logic and API interactions
│   └── utils                 # Utility functions and helpers
├── tests                     # Directory containing test files for the bot
├── .env                      # Environment variables for the bot
├── requirements.txt          # List of required Python packages
├── setup.py                  # Packaging information for the bot
└── README.md                 # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd discord-bot-gemini
   ```

2. **Install dependencies:**
   Ensure you have Python 3.8 or higher installed. Then, install the required packages using pip:
   ```
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the root directory and add your Discord bot token and any other necessary API keys:
   ```
   DISCORD_LLM_BOT_TOKEN=<your-discord-bot-token>
   GEMINI_API_URL=<your-gemini-api-url>
   ```

4. **Run the bot:**
   Start the bot by executing the following command:
   ```
   python src/bot.py
   ```

## Usage Guidelines

- The bot responds to user messages and commands based on the functionalities defined in the cogs.
- You can customize the bot's behavior by modifying the cog files located in the `src/cogs` directory.
- The bot utilizes the Gemini API for processing requests and generating responses.

## Features

- **Dynamic Interaction:** The bot can engage users in conversations, providing personalized responses.
- **Modular Design:** The use of cogs allows for easy addition and management of functionalities.
- **API Integration:** The bot interacts with the Gemini API to enhance its capabilities.

## Testing

To ensure the bot functions as expected, unit tests are provided in the `tests` directory. You can run the tests using:
```
pytest
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## 🔗 Relationship System

### Tính Năng Mới Đã Thêm

**RelationshipService** - Hệ thống theo dõi mối quan hệ thông minh:

#### 🤖 Tự Động Phát Hiện
- **Mentions & Tags**: Theo dõi ai tag ai, tần suất tương tác
- **Mối quan hệ**: Tự động nhận diện khi user nói về relationships
  - "Quang với Hoà là bạn" 
  - "Tôi thích Linh"
  - "Nam ghét Tom"
  - "Anna và Bob đang hẹn hò"
- **Thông tin tên**: Tự động cập nhật username, display name, tên thật
- **Lịch sử hội thoại**: Lưu trữ và tóm tắt cuộc trò chuyện

#### 📱 Lệnh Mới
```bash
!relationships [user]     # Xem mối quan hệ 
!conversation user1 user2 # Tóm tắt cuộc trò chuyện
!analysis [user]          # Phân tích AI về relationships
!search_relations keyword # Tìm kiếm theo từ khóa
!mentions user1 user2     # Lịch sử tag giữa 2 người
!all_users               # Tóm tắt tất cả users (admin)
```

#### 🎯 Trải Nghiệm Chat Thông Minh
- Bot nhớ và sử dụng tên thật thay vì username
- Hiểu context relationships khi trò chuyện
- Phân biệt người dùng khi có tên trùng nhau
- Đưa ra lời khuyên phù hợp dựa trên mối quan hệ

#### 📚 Documentation
- **[RELATIONSHIP_GUIDE.md](RELATIONSHIP_GUIDE.md)** - Hướng dẫn sử dụng cho user
- **[RELATIONSHIP_TECHNICAL_DOCS.md](RELATIONSHIP_TECHNICAL_DOCS.md)** - Technical documentation

#### 🧪 Testing
```bash
python test_relationship_service.py  # Test offline functionality
```