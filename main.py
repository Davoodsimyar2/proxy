# فایل: server.py
import asyncio
import websockets

# گوشی باید به این WebSocket متصل شود
# و داده‌ها را به اینترنت ارسال کند

connected_phone = None

async def relay(websocket, path):
    global connected_phone
    connected_phone = websocket
    print("Phone connected")
    try:
        async for message in websocket:
            # message از کامپیوتر می‌آید
            if connected_phone:
                await connected_phone.send(message)
    except:
        print("Phone disconnected")
        connected_phone = None

start_server = websockets.serve(relay, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
