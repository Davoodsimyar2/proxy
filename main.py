# server.py
import asyncio
import os
import websockets
import traceback

# پورت از Render environment یا 10000
PORT = int(os.environ.get("PORT", 10000))

# نگه داشتن اتصال گوشی (یا موبایل) برای relay
connected_phone = None

async def relay_handler(websocket, path):
    global connected_phone
    print(f"[NEW WS CONNECTION] path={path}")

    try:
        if path == "/phone":  # گوشی به /phone وصل می‌شود
            connected_phone = websocket
            print("[PHONE] Connected successfully")
            async for message in websocket:
                print(f"[PHONE → SERVER] {len(message)} bytes")
            print("[PHONE] Disconnected")
            connected_phone = None

        elif path == "/browser":  # مرورگر کامپیوتر به /browser وصل می‌شود
            print("[BROWSER] Connected")
            if connected_phone is None:
                print("[WARNING] Phone not connected yet! Data won't be relayed.")
            async for message in websocket:
                print(f"[BROWSER → SERVER] {len(message)} bytes")
                if connected_phone:
                    try:
                        await connected_phone.send(message)
                        print(f"[SERVER → PHONE] Sent {len(message)} bytes")
                    except Exception as e:
                        print("[ERROR] Sending to phone:", e)
                else:
                    print("[WARNING] Phone not connected, dropping data.")
            print("[BROWSER] Disconnected")
        else:
            print("[INFO] Unknown path:", path)
            await websocket.close()
    except Exception as e:
        print("[ERROR] Exception in relay_handler:", e)
        traceback.print_exc()

async def main():
    print(f"[STARTING] WebSocket server on port {PORT}")
    server = await websockets.serve(relay_handler, "0.0.0.0", PORT)
    print("[READY] Server is running...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
