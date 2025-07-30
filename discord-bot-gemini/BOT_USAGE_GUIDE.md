# 🤖 Discord Bot với Gemini AI - Hướng dẫn sử dụng

## 📋 Tính năng chính

### 💬 Trò chuyện thông minh
- Bot sử dụng nhân cách **Gemini** - cô gái tóc hồng, mắt dị sắc, mê chụp ảnh
- Phản hồi ngắn gọn, đồng cảm và thân thiện
- Nhớ được ngữ cảnh hội thoại

### 📝 Lưu trữ và tóm tắt
- **Lưu lịch sử hội thoại**: Tự động lưu mọi cuộc trò chuyện
- **Tóm tắt thông tin**: Tự động tạo summary về người dùng
- **Cập nhật thông minh**: Cập nhật thông tin khi có thay đổi quan trọng

## 🎯 Cách sử dụng

### Trò chuyện cơ bản
```
@Bé Bảy xin chào!           # Mention bot để trò chuyện
```

### Commands cơ bản
```
!ping                       # Test bot có hoạt động không
!status                     # Xem trạng thái bot
!respond <tin nhắn>         # Bắt buộc bot phản hồi
!chat <tin nhắn>           # Trò chuyện bằng command
```

### Commands quản lý summary
```
!summary                    # Xem tóm tắt thông tin của bạn
!summary @user             # Xem tóm tắt của user khác
!update_summary            # Cập nhật tóm tắt ngay lập tức
!clear_summary             # Xóa tóm tắt
!history_stats             # Xem thống kê lịch sử hội thoại
```

### Commands quản lý channel (Admin)
```
!enable_here               # Cho phép bot hoạt động trong channel này
!everywhere                # Cho phép bot hoạt động ở mọi channel
!debug                     # Xem thông tin debug
```

## 🔧 Tính năng nâng cao

### Tự động tóm tắt
Bot sẽ tự động tạo và cập nhật tóm tắt khi:
- Có thông tin quan trọng (tên, tuổi, sở thích...)
- Có thay đổi về tâm trạng, mối quan hệ
- Đủ tin nhắn để phân tích (tối thiểu 4 tin nhắn)

### Nhớ ngữ cảnh
- Bot nhớ 3 cuộc trò chuyện gần nhất
- Sử dụng thông tin tóm tắt để phản hồi phù hợp
- Cập nhật liên tục theo thời gian thực

## 📊 Các từ khóa quan trọng
Bot sẽ đặc biệt chú ý đến:
- **Thông tin cơ bản**: tên, tuổi, sinh nhật
- **Sở thích**: thích, yêu, mê, hobby
- **Tâm trạng**: buồn, vui, stress, hạnh phúc
- **Mối quan hệ**: độc thân, người yêu, chia tay
- **Ước mơ**: muốn, ước, dự định, kế hoạch

## 🚀 Ví dụ sử dụng

```
User: @Bé Bảy xin chào, tôi tên là An
Bot: Chào An! Rất vui được gặp bạn! ✨

User: Tôi 22 tuổi, thích chụp ảnh phong cảnh
Bot: Woa, cùng sở thích với mình đây! 📸 Bạn hay chụp ảnh ở đâu?

User: !summary
Bot: [Hiển thị tóm tắt]
📋 Tóm tắt thông tin - An
- Tên: An
- Tuổi: 22
- Sở thích: Chụp ảnh phong cảnh
```

## ⚙️ Cấu hình

Bot sẽ phản hồi khi:
1. **Được mention** trong bất kỳ channel nào
2. **Trong DM** (tin nhắn riêng)
3. **Trong channel được cấu hình** (nếu có)

Để cấu hình channel: `!enable_here` hoặc `!everywhere`
