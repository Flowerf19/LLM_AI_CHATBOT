# 🔗 RelationshipService Technical Documentation

## Tổng Quan

RelationshipService là một hệ thống AI-powered để theo dõi và phân tích mối quan hệ giữa các thành viên trong Discord server. Nó tự động nhận diện, lưu trữ và phân tích các tương tác xã hội để tạo ra trải nghiệm chat thông minh hơn.

## Kiến Trúc Hệ Thống

```
RelationshipService
├── Data Storage (JSON files)
│   ├── relationships.json      # Mối quan hệ giữa users
│   ├── user_names.json        # Mapping tên/ID
│   ├── interactions.json      # Lịch sử tương tác
│   └── conversation_history.json # Lịch sử hội thoại
├── Pattern Recognition
│   ├── Relationship extraction
│   ├── Name detection
│   └── Mention tracking
└── AI Analysis
    ├── Relationship insights
    └── Social behavior analysis
```

## Core Components

### 1. Data Models

#### User Names Structure
```json
{
  "user_id": {
    "username": "discord_username",
    "display_name": "Display Name",
    "real_name": "Real Name",
    "name_history": ["old_name1", "old_name2"],
    "first_seen": "2025-01-01T00:00:00",
    "last_updated": "2025-01-01T12:00:00"
  }
}
```

#### Relationships Structure
```json
{
  "person1_person2": {
    "person1": "Name1",
    "person2": "Name2", 
    "relationship_history": [
      {
        "type": "friend|crush|romantic|ex|dislike",
        "reported_by": "user_id",
        "context": "original message context",
        "confidence": 0.8,
        "timestamp": "2025-01-01T12:00:00"
      }
    ]
  }
}
```

#### Interactions Structure
```json
{
  "from_user_to_user": {
    "from_user": "user_id1",
    "to_user": "user_id2",
    "interactions": [
      {
        "type": "mention|reply|tag",
        "timestamp": "2025-01-01T12:00:00",
        "context": "message context"
      }
    ]
  }
}
```

### 2. Pattern Recognition

#### Relationship Patterns
Hệ thống nhận diện các pattern sau:

```python
relationship_patterns = [
    r'(\w+)\s+(?:và|với)\s+(\w+)\s+(?:là|are)\s+(?:bạn|friends?)',  # "A và B là bạn"
    r'(\w+)\s+(?:thích|likes?)\s+(\w+)',                           # "A thích B"
    r'(\w+)\s+(?:ghét|hates?)\s+(\w+)',                           # "A ghét B" 
    r'(\w+)\s+(?:là\s+)?(?:người\s+yêu|boyfriend|girlfriend)\s+(?:của\s+)?(\w+)', # "A là người yêu của B"
    r'(\w+)\s+(?:đang\s+)?(?:hẹn\s+hò|dating)\s+(?:với\s+)?(\w+)', # "A đang hẹn hò với B"
    r'(\w+)\s+(?:chia\s+tay|broke\s+up)\s+(?:với\s+)?(\w+)'       # "A chia tay với B"
]
```

#### Name Patterns
```python
name_patterns = [
    r'tên\s+(tôi|mình|em)\s+(?:là\s+)?(\w+)',     # "tên tôi là X"
    r'(?:tôi|mình|em)\s+tên\s+(?:là\s+)?(\w+)',   # "tôi tên X"
    r'(?:gọi|call)\s+(?:tôi|mình|em)\s+(?:là\s+)?(\w+)', # "gọi tôi là X"
    r'(\w+)\s+tên\s+(?:thật\s+)?(?:là\s+)?(\w+)'  # "A tên thật là B"
]
```

### 3. API Methods

#### Core Methods
- `process_message()`: Xử lý tin nhắn và extract thông tin
- `update_user_name()`: Cập nhật thông tin tên user
- `get_user_relationships()`: Lấy mối quan hệ của user
- `get_interaction_stats()`: Thống kê tương tác
- `generate_relationship_analysis()`: Phân tích AI

#### Utility Methods
- `get_user_display_name()`: Lấy tên hiển thị tốt nhất
- `_resolve_user_identifier()`: Resolve tên/ID về user ID
- `search_relationships_by_keyword()`: Tìm kiếm theo từ khóa
- `get_conversation_summary()`: Tóm tắt cuộc trò chuyện

## Integration với Bot

### 1. LLMMessageCog Integration

```python
# Trong __init__()
self.relationship_service = RelationshipService(self.gemini_service, data_dir)

# Trong _handle_message()
await self._process_relationship_data(message, content, user_id)

# Trong _build_enhanced_context()
user_relationships = self.relationship_service.get_user_relationships(user_id)
# Thêm relationship context vào AI prompt
```

### 2. Commands Integration

Các lệnh được tích hợp trong `UserCommandsCog`:
- `!relationships` - Xem mối quan hệ
- `!conversation` - Tóm tắt cuộc trò chuyện  
- `!analysis` - Phân tích AI
- `!search_relations` - Tìm kiếm
- `!mentions` - Lịch sử tag
- `!all_users` - Tóm tắt tất cả users (admin)

## Performance Considerations

### 1. Data Limits
- **Relationships**: Giữ 20 entries gần nhất per relationship
- **Interactions**: Giữ 100 interactions gần nhất per user pair
- **Conversations**: Giữ 50 messages gần nhất per conversation

### 2. Processing Efficiency
- **Real-time processing**: Xử lý tin nhắn ngay lập tức
- **Async operations**: Tất cả AI calls đều async
- **Memory optimization**: Không load toàn bộ data vào memory
- **File-based storage**: JSON files cho persistence đơn giản

### 3. Scaling
- **Horizontal scaling**: Có thể chuyển sang database
- **Data partitioning**: Có thể partition theo guild/server
- **Caching**: Có thể thêm Redis cho cache

## Security & Privacy

### 1. Data Protection
- **Local storage**: Chỉ lưu trữ local, không gửi ra ngoài
- **User consent**: Chỉ xử lý data công khai trong chat
- **Admin controls**: Admin có quyền xóa/quản lý data

### 2. Privacy Features
- **Anonymization**: Có thể anonymize sensitive data
- **Data retention**: Auto-cleanup old data
- **User rights**: User có thể request xóa data của mình

## Error Handling

### 1. Graceful Degradation
```python
try:
    # Relationship processing
    self._process_relationship_data(message, content, user_id)
except Exception as e:
    logger.error(f"Relationship processing failed: {e}")
    # Continue without relationship features
```

### 2. Data Validation
- **JSON validation**: Kiểm tra format trước khi save
- **Type checking**: Validate data types
- **Sanitization**: Clean user input

## Testing

### 1. Unit Tests
- Pattern recognition tests
- Data processing tests  
- API method tests

### 2. Integration Tests
- Full workflow tests
- Discord interaction tests
- Performance tests

### 3. Test Script
Sử dụng `test_relationship_service.py` để test offline:

```bash
python test_relationship_service.py
```

## Future Enhancements

### 1. Advanced Features
- **Sentiment analysis**: Phân tích cảm xúc trong relationships
- **Relationship strength**: Tính toán độ mạnh mối quan hệ
- **Social graph analysis**: Phân tích mạng xã hội
- **Recommendation system**: Gợi ý bạn bè/hoạt động

### 2. UI Improvements
- **Web dashboard**: Giao diện web để visualize relationships
- **Discord embeds**: Rich embeds cho commands
- **Interactive features**: Buttons, dropdowns trong Discord

### 3. AI Enhancements
- **Better NLP**: Sử dụng models chuyên về relationship extraction
- **Multi-language**: Hỗ trợ nhiều ngôn ngữ
- **Context awareness**: Hiểu context tốt hơn

## Troubleshooting

### Common Issues

1. **File permission errors**
   ```python
   # Đảm bảo thư mục có quyền write
   os.makedirs(self.relationships_dir, exist_ok=True)
   ```

2. **JSON corruption**
   ```python
   # Backup trước khi save
   if os.path.exists(file_path):
       shutil.copy(file_path, file_path + '.bak')
   ```

3. **Memory usage**
   ```python
   # Clean old data periodically
   if len(data) > MAX_ENTRIES:
       data = data[-MAX_ENTRIES:]
   ```

### Debug Commands

```python
# Log relationship processing
logger.debug(f"Processing relationship: {person1} -> {person2}")

# Validate data integrity
def validate_data_integrity(self):
    # Check for inconsistencies
    pass
```

---

*RelationshipService là core component cho social intelligence của bot. Thiết kế modular cho phép dễ dàng mở rộng và tùy chỉnh theo nhu cầu cụ thể.*
