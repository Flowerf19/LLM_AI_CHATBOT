# 🤖 Bot Channel Management Guide

## Slash Commands (Khuyến nghị)

### `/addbotchannel`
- **Mô tả**: Thêm kênh vào danh sách cho bot hoạt động **TỰ ĐỘNG**
- **Quyền**: Manage Channels
- **Sử dụng**: `/addbotchannel #kênh-chat`
- **Lưu ý**: Bot sẽ phản hồi TẤT CẢ tin nhắn trong kênh này (không cần tag)

### `/removebotchannel` 
- **Mô tả**: Xóa kênh khỏi danh sách bot
- **Quyền**: Manage Channels  
- **Sử dụng**: `/removebotchannel #kênh-chat`

### `/listbotchannels`
- **Mô tả**: Xem danh sách tất cả kênh bot
- **Quyền**: Không cần
- **Sử dụng**: `/listbotchannels`

### `/clearbotchannels`
- **Mô tả**: Xóa tất cả kênh bot (bot chỉ phản hồi khi được tag)
- **Quyền**: Manage Channels
- **Sử dụng**: `/clearbotchannels`

## Cách Bot Phản Hồi

### 🔹 Khi CHƯA thiết lập bot channels:
- Bot chỉ phản hồi khi được **@mention**
- Bot luôn phản hồi **tin nhắn riêng (DM)**

### 🔹 Khi ĐÃ thiết lập bot channels:
- **Trong kênh bot**: Bot phản hồi **TẤT CẢ** tin nhắn (không cần tag)
- **Kênh khác**: Bot chỉ phản hồi khi được **@mention**  
- **DM**: Bot luôn phản hồi

## Ví Dụ Hoạt Động

```
// Thêm #bot-chat làm kênh bot
/addbotchannel #bot-chat

// Bây giờ trong #bot-chat:
"Xin chào"           → Bot phản hồi ✅
"Hôm nay thế nào?"   → Bot phản hồi ✅
"!help"              → Chạy lệnh (không phản hồi bằng AI) ✅

// Trong kênh khác (#general):
"Xin chào"           → Bot KHÔNG phản hồi ❌
"@BotName xin chào"  → Bot phản hồi ✅
```

## Prefix Commands (Tương thích cũ)

- `!addbotchannel [#kênh]` - Thêm kênh bot
- `!removebotchannel [#kênh]` - Xóa kênh bot  
- `!listbotchannels` - Liệt kê kênh bot
- `!clearbotchannels` - Xóa tất cả kênh bot

## Cách Bot Hoạt Động

1. **Nếu chưa set kênh nào**: Bot hoạt động ở tất cả kênh
2. **Sau khi set kênh**: Bot chỉ hoạt động trong các kênh đã được thêm
3. **DM**: Bot luôn phản hồi tin nhắn riêng

## Ví Dụ Sử Dụng

```
// Thêm kênh #general cho bot
/addbotchannel #general

// Thêm kênh #bot-chat cho bot  
/addbotchannel #bot-chat

// Xem danh sách kênh
/listbotchannels

// Xóa kênh #general
/removebotchannel #general

// Cho phép bot hoạt động ở mọi kênh
/clearbotchannels
```

## Lưu Ý

- File cấu hình được lưu tại `src/data/bot_channels.json`
- Cần quyền "Manage Channels" để quản lý kênh bot
- Bot luôn phản hồi khi được mention hoặc trong DM
