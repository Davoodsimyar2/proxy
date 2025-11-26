from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# نگهداری داده‌ها بر اساس device_id و code
device_data = {}
device_timestamp = {}

def get_device_id(code):
    try:
        code = int(code)
        return code // 1000
    except:
        return None

@app.route("/data", methods=["POST"])
def receive_data():
    global device_data, device_timestamp

    data = request.json
    if not data or "code" not in data:
        return jsonify({"error": "missing 'code' field"}), 400

    code = int(data["code"])
    device_id = get_device_id(code)
    if device_id is None:
        return jsonify({"error": "invalid code"}), 400

    # اگر برای این device_id هنوز دیتایی نیست، بسازیم
    if device_id not in device_data:
        device_data[device_id] = {}
        device_timestamp[device_id] = {}

    # ذخیره آخرین نسخه برای code
    device_data[device_id][code] = data
    device_timestamp[device_id][code] = time.time()

    print(f"Device {device_id} code {code} updated:", data)
    return jsonify({"status": "success", "device_id": device_id, "code": code})

@app.route("/poll", methods=["GET"])
def poll():
    device_id = request.args.get("device_id")
    last = float(request.args.get("last", 0))

    if device_id is None:
        return jsonify({"error": "device_id missing"}), 400
    try:
        device_id = int(device_id)
    except:
        return jsonify({"error": "invalid device_id"}), 400

    timeout = 30
    start = time.time()

    while time.time() - start < timeout:
        response_data = {}
        if device_id in device_data:
            # فقط داده‌هایی که جدیدتر از last هستند
            for code, ts in device_timestamp[device_id].items():
                if ts > last:
                    response_data[code] = device_data[device_id][code]

        if response_data:
            # حداکثر timestamp را برای ارسال به ESP نگه می‌داریم
            max_ts = max(device_timestamp[device_id].values())
            return jsonify({"data": response_data, "timestamp": max_ts})

        time.sleep(0.5)

    return jsonify({"status": "no new data", "timestamp": last})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"devices": device_data, "timestamps": device_timestamp})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
