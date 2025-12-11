# server.py
import os
import asyncio
import base64
import json
from aiohttp import web, WSMsgType

# === مدیریت WebSocket ===
clients = set()
phone_connected = False
phone_ws = None

async def ws_handler(request):
    global phone_connected, phone_ws
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    clients.add(ws)
    print("[INFO] Client connected")
    await ws.send_str(json.dumps({"status":"connected"}))

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            cmd = data.get("cmd")

            if cmd == "phone_ip":
                print("[PHONE IP]", data.get("ip"))
            elif cmd == "fetch_result":
                rid = data.get("id")
                body_b64 = base64.b64encode(data.get("body","").encode()).decode()
                # می‌توانید اینجا به کامپیوتر بفرستید
            elif cmd == "register_phone":
                phone_connected = True
                phone_ws = ws
                print("[INFO] Phone connected")
        elif msg.type == WSMsgType.ERROR:
            print(f"[WS ERROR] {ws.exception()}")

    clients.remove(ws)
    print("[INFO] Client disconnected")
    if ws == phone_ws:
        phone_connected = False
        phone_ws = None
        print("[INFO] Phone disconnected")
    return ws

# === صفحه وب تست اتصال ===
async def index(request):
    ip_status = "connected" if phone_connected else "not connected"
    html = f"""
    <html>
        <head><title>Phone Proxy Status</title></head>
        <body>
            <h2>Phone Proxy Status</h2>
            <p>Phone connected: {ip_status}</p>
        </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

# === راه اندازی وب سرویس ===
app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/ws', ws_handler)

port = int(os.environ.get("PORT", 10000))
web.run_app(app, host="0.0.0.0", port=port)
