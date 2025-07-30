# ⌨️ Typing Simulation Feature

## Tổng Quan

Tính năng **Typing Simulation** giúp bot mô phỏng cách gõ phím tự nhiên của con người, tạo trải nghiệm chat chân thực hơn trên Discord.

## Tính Năng

### 🎯 Realistic Typing Behavior
- **Typing Indicator**: Hiển thị "đang nhập..." khi bot đang "gõ"
- **Natural Delays**: Delay dựa trên độ dài và độ phức tạp của message
- **Message Splitting**: Tách response thành nhiều parts tự nhiên
- **Variable Speed**: Tốc độ gõ có biến thiên như người thật

### 📝 Intelligent Message Splitting

Bot tự động tách response theo:
1. **Đoạn văn** (split by `\n\n`)
2. **Câu** (split by `.!?`) 
3. **Độ dài hợp lý** (max 200 chars per part)
4. **Discord limits** (max 2000 chars per message)

### ⚡ Typing Speed Calculation

```python
# Công thức tính delay
base_delay = text_length / chars_per_second
complexity_delay = emoji_count * 0.2 + punctuation_count * 0.1
total_delay = (base_delay + complexity_delay) * random_factor
```

### 🎛️ Configurable Settings

Tất cả settings có thể tùy chỉnh trong `.env`:

```env
ENABLE_TYPING_SIMULATION=1    # Bật/tắt tính năng
TYPING_SPEED_WPM=250         # Tốc độ gõ (words/minute)
MIN_TYPING_DELAY=0.5         # Delay tối thiểu (giây)
MAX_TYPING_DELAY=8.0         # Delay tối đa (giây)
PART_BREAK_DELAY=0.6         # Delay giữa các parts (giây)
```

## Ví Dụ Hoạt Động

### Before (Không có typing simulation)
```
User: xin chào
Bot: Chào bạn! Đây là một câu trả lời dài có thể được gửi ngay lập tức mà không có delay nào cả.
```

### After (Có typing simulation)
```
User: xin chào
[Bot đang nhập...]                    # 1.2s delay
Bot: Chào bạn! 😊
[Bot đang nhập...]                    # 0.8s delay  
Bot: Đây là một câu trả lời dài
[Bot đang nhập...]                    # 1.5s delay
Bot: có thể được tách thành nhiều parts tự nhiên!
```

## Commands

### Test Commands
```bash
!test_typing              # Test typing simulation
!typing_settings          # Xem settings hiện tại (admin)
```

### Example Output
```
!test_typing

[Bot đang nhập...]
Bot: Đây là test typing effect! 😊

[Bot đang nhập...]  
Bot: Câu này sẽ được gửi riêng lẻ với typing delay tự nhiên.

[Bot đang nhập...]
Bot: Và cuối cùng là câu này! (づ｡◕‿‿◕｡)づ
```

## Technical Implementation

### Core Methods

#### `send_response_in_parts()`
- Main method xử lý typing simulation
- Check config để enable/disable
- Gọi các helper methods

#### `_split_response_naturally()`
- Tách response thành parts tự nhiên
- Ưu tiên paragraph > sentence > length
- Đảm bảo không vượt Discord limits

#### `_calculate_typing_delay()`
- Tính delay dựa trên text complexity
- Factor in emoji, punctuation, length
- Apply randomness cho natural feel

### Configuration Integration

```python
from config.settings import Config

# Check if enabled
if not Config.ENABLE_TYPING_SIMULATION:
    # Send normally
    await message.reply(response)
    return

# Use configured delays
delay = max(Config.MIN_TYPING_DELAY, min(Config.MAX_TYPING_DELAY, calculated_delay))
```

## Performance Considerations

### ⚡ Optimizations
- **Async operations**: Không block other messages
- **Reasonable limits**: Min/max delays prevent extreme cases
- **Disable option**: Có thể tắt hoàn toàn nếu cần

### 📊 Realistic Metrics
- **Typing Speed**: 150-300 WPM (realistic human range)
- **Message Length**: Split at 200 chars for natural feel
- **Complexity Factors**: Emoji +0.2s, punctuation +0.1s each

## Troubleshooting

### Common Issues

1. **Typing quá chậm**
   ```env
   TYPING_SPEED_WPM=300     # Tăng tốc độ
   MAX_TYPING_DELAY=5.0     # Giảm delay max
   ```

2. **Typing quá nhanh**
   ```env
   TYPING_SPEED_WPM=150     # Giảm tốc độ
   MIN_TYPING_DELAY=1.0     # Tăng delay min
   ```

3. **Muốn tắt typing**
   ```env
   ENABLE_TYPING_SIMULATION=0
   ```

4. **Message parts quá ngắn/dài**
   - Điều chỉnh logic trong `_split_response_naturally()`
   - Thay đổi threshold 200 chars

### Debug Commands

```python
# Log typing calculations
logger.debug(f"Typing delay for '{text[:50]}...': {delay:.2f}s")

# Test specific scenarios
await self.send_response_in_parts(message, "Test message with emoji 😊🎉!", user_id)
```

## Best Practices

### 🎯 Recommended Settings

**For fast servers:**
```env
TYPING_SPEED_WPM=300
MIN_TYPING_DELAY=0.3
MAX_TYPING_DELAY=5.0
PART_BREAK_DELAY=0.4
```

**For casual servers:**
```env
TYPING_SPEED_WPM=250  
MIN_TYPING_DELAY=0.5
MAX_TYPING_DELAY=8.0
PART_BREAK_DELAY=0.6
```

**For role-play servers:**
```env
TYPING_SPEED_WPM=180
MIN_TYPING_DELAY=1.0  
MAX_TYPING_DELAY=12.0
PART_BREAK_DELAY=1.0
```

### 💡 Tips

1. **Test với người dùng thật** để điều chỉnh settings
2. **Monitor performance** với large servers
3. **Có option tắt** cho emergency situations
4. **Document settings** cho team members

## Future Enhancements

### 🚀 Planned Features
- **User-specific typing speed**: Mỗi user có typing pattern riêng
- **Emotion-based delays**: Sad responses slower, excited faster  
- **Adaptive learning**: Bot học typing pattern từ user interactions
- **Voice message simulation**: Typing + "recording audio" indicator

### 🎨 Advanced Customization
- **Per-channel settings**: Different speeds cho different channels
- **Time-based variation**: Slower at night, faster in peak hours
- **Content-aware delays**: Technical responses slower than casual chat

---

*Typing Simulation tạo ra trải nghiệm chat tự nhiên và immersive hơn, giúp bot cảm thấy như một người bạn thật sự! ⌨️✨*
