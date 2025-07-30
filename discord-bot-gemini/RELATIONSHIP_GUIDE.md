# 🔗 Hướng Dẫn Sử Dụng Relationship System

## Tổng Quan
Relationship System giúp bot theo dõi và hiểu mối quan hệ giữa các thành viên trong server, tạo ra những cuộc trò chuyện tự nhiên và có ngữ cảnh hơn.

## Tính Năng Chính

### 1. 🤖 Tự Động Theo Dõi
Bot tự động theo dõi:
- **Mentions/Tags**: Ai tag ai, tần suất tag
- **Thông tin tên**: Username, display name, tên thật
- **Mối quan hệ**: Khi ai đó nói "A và B là bạn", "tôi thích C", v.v.
- **Cuộc trò chuyện**: Lưu trữ tóm tắt các cuộc trò chuyện

### 2. 📝 Phát Hiện Mối Quan Hệ
Bot nhận biết khi bạn nói:
- "Quang với Hoà là bạn"
- "Tôi thích Linh"  
- "Tôi tên Minh" (cập nhật tên thật)
- "Nam ghét Tom"
- "Anna và Bob đang hẹn hò"
- "Tôi chia tay với ex"

### 3. 🎯 Tên Thông Minh
- **Ưu tiên tên thật**: Gọi "Minh" thay vì "user123"
- **Phân biệt trùng tên**: Dùng user ID để phân biệt
- **Cập nhật linh hoạt**: Tự động cập nhật khi có thông tin mới

## Lệnh Sử Dụng

### !relationships [tên_user]
Xem mối quan hệ của bản thân hoặc người khác
```
!relationships
!mq Minh
!relation @user
```

### !conversation <user1> [user2] [số_ngày]
Xem tóm tắt cuộc trò chuyện
```
!conversation Minh Hoà 7
!cv @user1 @user2
!convo Linh  (với chính mình)
```

### !analysis [tên_user]
Phân tích mối quan hệ bằng AI
```
!analysis
!phântích Minh
!analyze @user
```

### !search_relations <từ_khóa>
Tìm kiếm mối quan hệ theo từ khóa
```
!search_relations bạn
!sr crush
!tìm hẹn hò
```

### !mentions <user1> <user2>
Xem lịch sử tag giữa hai người
```
!mentions Minh Hoà
!tag @user1 @user2
```

### !all_users (Admin only)
Xem tóm tắt tất cả users trong hệ thống
```
!all_users
!users
!members
```

## Ví Dụ Thực Tế

### Kịch Bản 1: Giới Thiệu Tên
```
Linh: Tôi tên Linh nhé bot
Bot: Chào Linh! Rất vui được biết tên thật của cậu 😊

Hoà: Gọi tôi là Hoà đi
Bot: Dạ, chào Hoà! 
```

### Kịch Bản 2: Nói Về Mối Quan Hệ  
```
Linh: Quang với Hoà là bạn thân của tôi
Bot: Ôi vậy hả! Linh có nhiều bạn thân ghê 😊

[Sau đó khi Linh nhắc đến Quang]
Linh: Hôm qua Quang buồn quá
Bot: Ôi Quang bạn thân cậu à? Chuyện gì vậy?
```

### Kịch Bản 3: Hỏi Về Cuộc Trò Chuyện
```
Linh: Tối qua Quang với Hoà nói gì thế?
Bot: Họ có nói về game mới và kế hoạch đi chơi cuối tuần. Quang có vẻ hứng thú với game đó, còn Hoà thì muốn đi ăn trước.
```

### Kịch Bản 4: Tag Thường Xuyên
```
[Linh thường xuyên tag Hoà]
Bot: Thấy Linh với Hoà chat nhiều ghê! Hai bạn thân thiết quá 😄
```

## Tips & Tricks

### 🎯 Tối Ưu Hóa
1. **Nói rõ mối quan hệ**: "A là bạn của B" thay vì "A biết B"
2. **Dùng tên thật**: Giúp bot nhớ và gọi tên đúng
3. **Tag thường xuyên**: Giúp bot hiểu mức độ thân thiết
4. **Cập nhật thay đổi**: Nói khi có thay đổi trong mối quan hệ

### 🔒 Quyền Riêng Tư
- Bot chỉ theo dõi thông tin công khai trong chat
- Admin có thể xem tất cả dữ liệu
- User thường chỉ xem được của mình và những gì được public

### ⚡ Hiệu Suất
- Bot xử lý real-time, không cần chờ đợi
- Dữ liệu được lưu trữ tự động
- Hệ thống tối ưu cho server lớn

## Troubleshooting

### Lỗi Thường Gặp
1. **"Relationship service không khả dụng"**: Bot đang restart hoặc có lỗi
2. **"Không tìm thấy người dùng"**: Kiểm tra tên/ID có đúng không
3. **"Chưa có thông tin"**: Cần thời gian để bot thu thập dữ liệu

### Liên Hệ Hỗ Trợ
- Dùng `!status` để kiểm tra tình trạng bot
- Tag admin nếu có vấn đề nghiêm trọng
- Báo cáo bug qua DM với admin

---

*Relationship System được thiết kế để tăng cường trải nghiệm chat tự nhiên và thông minh hơn. Hãy sử dụng một cách có trách nhiệm! 🤖💕*
