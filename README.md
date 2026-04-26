# Chat Server (FastAPI + Admin Web UI + iOS Client)

Một hệ thống chat realtime đơn giản gồm:
- Backend FastAPI (Python)
- Admin Web UI để đọc và trả lời tin nhắn
- Client iOS (Objective-C) kết nối qua HTTP

---

## 🚀 Tính năng

### Backend
- API gửi tin nhắn `/send`
- API lấy chat user `/chat`
- API admin xem chat `/admin_chat`
- API danh sách user `/users`
- Cache nhẹ để giảm load

### Admin Web
- Xem danh sách user
- Xem hội thoại theo từng user
- Gửi tin nhắn trả lời trực tiếp
- Auto refresh realtime (polling)

### iOS Client
- Giao diện chat mini floating view
- Tự động sync tin nhắn
- Gửi / nhận message qua HTTP
- Bubble chat user/admin

---

## 📦 Cài đặt

### 1. Cài Python dependencies

```bash
pip install fastapi uvicorn
