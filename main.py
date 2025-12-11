import asyncio
import base64
from aiohttp import web
import websockets

# نگهداری WebSocket گوشی
connected_phone = None

async def ws_phone_handler(ws, path):
    global connected_phone
    print("[PHONE] گوشی وصل شد")
    connected_phone = ws
    try:
        async for message in ws:
            # پیام‌ها از گوشی (در صورت نیاز می‌توان مدیریت کرد)
            print("[PHONE] پیام دریافت شد:", message)
    except Exception as e:
        print("[PHONE ERROR]", e)
    finally:
        print("[PHONE] گوشی قطع شد")
        connected_phone = None

# صفحه اصلی برای نمایش IP واقعی گوشی
async def index(request):
    if connected_phone:
        try:
            # درخواست IP از گوشی بخواهیم
            await connected_phone.send("GET_IP")
            ip = await connected_phone.recv()
        except Exception as e:
            ip = f"خطا: {e}"
    else:
        ip = "گوشی وصل نیست"

    html = f"""
    <html>
        <head><title>Proxy Status</title></head>
        <body>
            <h2>وضعیت اتصال اینترنت گوشی</h2>
            <p>IP اینترنت گوشی: {ip}</p>
            <p>وضعیت: {"وصل است" if connected_phone else "قطع است"}</p>
        </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

# مسیر fetch از کامپیوتر، پیام را به گوشی می‌فرستیم و جواب را دریافت می‌کنیم
async def fetch_url(request):
    if connected_phone is None:
        return web.json_response({"error": "گوشی وصل نیست"}, status=400)

    url = request.query.get("url")
    if not url:
        return web.json_response({"error": "پارامتر url موجود نیست"}, status=400)

    try:
        # به گوشی بفرستیم که URL را باز کند
        await connected_phone.send(url)
        content_b64 = await connected_phone.recv()
        return web.json_response({"body_b64": content_b64})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def main():
    # راه‌اندازی وب
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/fetch', fetch_url)

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(web.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    print(f"[WEB] Running on port {port}")

    # WebSocket گوشی روی پورت 8765
    ws_server = await websockets.serve(ws_phone_handler, "0.0.0.0", 8765)
    print("[WS] WebSocket for phone running on port 8765")

    await site.start()
    await asyncio.Future()  # نگه داشتن سرور

asyncio.run(main())
