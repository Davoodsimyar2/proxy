from flask import Flask, request, jsonify

app = Flask(__name__)

# یک endpoint ساده برای دریافت داده‌ها
@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json  # داده JSON که از اپلیکیشن می‌آید
    print("Received data:", data)  # چاپ داده‌ها در لاگ Render
    return jsonify({"status": "success", "received": data})

# یک endpoint برای تست دستی در مرورگر
@app.route("/", methods=["GET"])
def home():
    return "Server is running! Use POST /data to send JSON."

if __name__ == "__main__":
    # با Render، پورت از محیط می‌آید
    import os
    port = int(os.environ.get("PORT", 10000))  # اگر PORT ندادند، 10000
    app.run(host="0.0.0.0", port=port)
