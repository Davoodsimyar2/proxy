import os
import base64
import aiohttp
from aiohttp import web

PORT = int(os.environ.get("PORT", 10000))

async def fetch_handler(request):
    url = request.query.get("url")
    if not url:
        return web.json_response({"error": "missing url"}, status=400)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                body = await resp.read()
                return web.json_response({
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body_b64": base64.b64encode(body).decode()
                })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def index(request):
    return web.Response(text="Python proxy server is running.\nUse /fetch?url=<...>")

app = web.Application()
app.add_routes([
    web.get('/', index),
    web.get('/fetch', fetch_handler),
])

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=PORT)
