from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
import time

app = FastAPI()

# Lưu trữ tin nhắn: { user_id: [messages] }
messages = {}

# Cache cho phía User
chat_cache = {}
chat_cache_time = {}
CACHE_TTL = 1.0


# ================= SEND MESSAGE =================
@app.post("/send")
async def send(req: Request):
    data = await req.json()
    user_id = data.get("user_id")
    msg = data.get("msg")
    role = data.get("role", "user")

    if not user_id or not msg:
        return {"status": "error"}

    messages.setdefault(user_id, []).append({
        "role": role,
        "msg": msg,
        "ts": time.time()
    })

    # Xóa cache để user nhận được tin ngay lập tức
    chat_cache.pop(user_id, None)
    return {"status": "ok"}


# ================= USER CHAT (Dùng cho iOS/Client) =================
@app.get("/chat")
async def chat(user_id: str = Query(...)):
    now = time.time()
    if user_id in chat_cache and now - chat_cache_time.get(user_id, 0) < CACHE_TTL:
        return chat_cache[user_id]

    data = messages.get(user_id, [])
    chat_cache[user_id] = data
    chat_cache_time[user_id] = now
    return data


# ================= ADMIN GET CHAT (Fix lỗi không thấy tin nhắn) =================
@app.get("/admin_chat")
async def admin_chat(user_id: str = Query(...)):
    # Admin lấy trực tiếp từ data gốc, không qua cache
    return messages.get(user_id, [])


# ================= USERS LIST =================
@app.get("/users")
async def users():
    return list(messages.keys())


# ================= ADMIN PAGE =================
@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Admin Chat Control</title>
    <style>
        body { margin:0; font-family:sans-serif; background:#111; color:white; overflow:hidden; }
        #container { display:flex; height:100vh; }
        #users { width:240px; border-right:1px solid #333; overflow-y:auto; background:#181818; }
        .user { padding:15px; cursor:pointer; border-bottom:1px solid #222; font-size:14px; transition:0.2s; }
        .user:hover { background:#282828; }
        .user.active { background:#0084ff; color:white; }
        #chat { flex:1; display:flex; flex-direction:column; background:#111; }
        #messages { flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; }
        .msg { padding:10px 14px; margin:5px 0; border-radius:15px; max-width:70%; word-break:break-word; font-size:14px; line-height:1.4; }
        .userMsg { background:#333; align-self: flex-start; border-bottom-left-radius:2px; }
        .adminMsg { background:#0084ff; align-self: flex-end; border-bottom-right-radius:2px; }
        #inputBox { display:flex; border-top:1px solid #333; padding:15px; background:#181818; }
        #input { flex:1; padding:12px; border:none; background:#222; color:white; border-radius:5px; outline:none; }
        button { background:#0084ff; border:none; color:white; padding:0 20px; margin-left:10px; cursor:pointer; border-radius:5px; font-weight:bold; }
        button:hover { background:#0073e6; }
    </style>
</head>
<body>
<div id="container">
    <div id="users"></div>
    <div id="chat">
        <div id="messages"></div>
        <div id="inputBox">
            <input id="input" placeholder="Nhập tin nhắn..." onkeypress="if(event.keyCode==13) send()">
            <button onclick="send()">GỬI</button>
        </div>
    </div>
</div>

<script>
let currentUser = null;
let lastMsgCount = 0;

async function loadUsers() {
    try {
        let res = await fetch('/users');
        let data = await res.json();
        let box = document.getElementById('users');
        
        // Chỉ vẽ lại nếu số lượng user thay đổi hoặc chưa có user nào
        if (data.length !== box.children.length) {
            box.innerHTML = '';
            data.forEach(u => {
                let div = document.createElement('div');
                div.className = 'user' + (currentUser === u ? ' active' : '');
                div.innerText = u;
                div.onclick = () => {
                    document.querySelectorAll('.user').forEach(el => el.classList.remove('active'));
                    div.classList.add('active');
                    currentUser = u;
                    lastMsgCount = 0; // Reset để load lại chat ngay
                    loadChat();
                };
                box.appendChild(div);
            });
        }
    } catch(e) {}
}

async function loadChat() {
    if (!currentUser) return;
    try {
        let res = await fetch('/admin_chat?user_id=' + currentUser);
        let data = await res.json();
        
        // Chỉ cập nhật UI nếu có tin nhắn mới
        if (data.length !== lastMsgCount) {
            let box = document.getElementById('messages');
            box.innerHTML = '';
            data.forEach(m => {
                let div = document.createElement('div');
                div.className = 'msg ' + (m.role === 'admin' ? 'adminMsg' : 'userMsg');
                div.innerText = m.msg;
                box.appendChild(div);
            });
            box.scrollTop = box.scrollHeight;
            lastMsgCount = data.length;
        }
    } catch(e) {}
}

async function send() {
    if (!currentUser) return;
    let input = document.getElementById('input');
    let msg = input.value.trim();
    if (!msg) return;

    await fetch('/send', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            user_id: currentUser,
            role: 'admin',
            msg: msg
        })
    });

    input.value = '';
    loadChat();
}

// Chạy vòng lặp cập nhật
setInterval(loadUsers, 2000);
setInterval(loadChat, 1000);
</script>
</body>
</html>
"""

# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    # Chạy trên port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
