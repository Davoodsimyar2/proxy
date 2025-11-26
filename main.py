from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# آخرین داده و زمان دریافت
last_data = {}
last_update = 0  # timestamp آخرین داده

@app.route("/data", methods=["POST"])
def receive_data():
    """دریافت داده جدید از ESP یا کلاینت دیگر"""
    global last_data, last_update
    last_data = request.json
    last_update = time.time()  # ثبت زمان دریافت
    print("Received data:", last_data)
    return jsonify({"status": "success", "received": last_data})

@app.route("/", methods=["GET"])
def home():
    """نمایش داده آخر در مرورگر"""
    if last_data:
        return f"""
        <h2>آخرین داده دریافتی:</h2>
        <pre>{last_data}</pre>
        """
    else:
        return "<h3>هنوز هیچ داده‌ای دریافت نشده است.</h3>"

@app.route("/poll", methods=["GET"])
def poll():
    """Long Polling endpoint"""
    global last_data, last_update
    timeout = 30  # ثانیه، حداکثر انتظار
    start = time.time()

    # گرفتن آخرین timestamp که ESP دریافت کرده
    last_received = float(request.args.get("last", 0))

    while time.time() - start < timeout:
        if last_update > last_received:  # داده جدید بعد از آخرین دریافت
            return jsonify({"data": last_data, "timestamp": last_update})
        time.sleep(0.5)

    # هیچ داده جدیدی نیامده
    return jsonify({"status": "no new data", "timestamp": last_received})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
