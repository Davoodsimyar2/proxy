import asyncio
import websockets
import json
from flask import Flask, request
import threading
import os

app = Flask(__name__)

# آخرین WebSocket گوشی
phone_ws = None

# برای نگه‌داشتن آخرین اینترنت گوشی
last_phone_ip = None


# ========== وب‌سوکت گوشی ==========
async def phone_handler(websocket):
    global phone_ws, last_phone_ip
    phone_ws = websocket
    print("PHONE CONNECTED")

    # از گوشی IP بگیریم
    await websocket.send(json.dumps({"cmd": "get_ip"}))

    try:
        async for msg in websocket:
            data = json.loads(msg)

            if data["cmd"] == "phone_ip":
                last_phone_ip = data["ip"]

            elif data["cmd"] == "fetch_result":
                request_id = data["id"]
                body = data.get("body", "")
                fetch_waiters[request_id].set_result(body)

    except:
        print("PHONE DISCONNECTED")
    finally:
        phone_ws = None


async def ws_server():
    async with websockets.serve(phone_handler, "0.0.0.0", 8001):
        await asyncio.Future()


# ========== سرور HTTP برای کامپیوتر ==========
fetch_waiters = {}

@app.route("/")
def index():
    connected = "YES" if phone_ws else "NO"
    ip = last_phone_ip or "Unknown"

    return f"""
    <html>
    <body>
        <h2>Phone Proxy Status</h2>
        <p>Phone Connected: <b>{connected}</b></p>
        <p>Phone Internet IP: <b>{ip}</b></p>
        <p>Use: /fetch?url=https://example.com</p>
    </body>
    </html>
    """

@app.route("/fetch")
def fetch_url():
    global phone_ws

    if not phone_ws:
        return "Phone not connected!", 503

    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    # ارسال درخواست به گوشی
    req_id = os.urandom(4).hex()
    waiter = asyncio.get_event_loop().create_future()
    fetch_waiters[req_id] = waiter

    asyncio.get_event_loop().create_task(
        phone_ws.send(json.dumps({"cmd": "fetch", "id": req_id, "url": url}))
    )

    # منتظر جواب گوشی
    body = asyncio.get_event_loop().run_until_complete(waiter)

    return body


# ========== اجرای همزمان Flask + WebSocket ==========
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

asyncio.get_event_loop().run_until_complete(ws_server())
