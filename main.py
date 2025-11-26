from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# نگهداری داده هر ESP
# مثال: device_data[0] → آخرین پیام ESP شماره 0
device_data = {}

# زمان آخرین آپدیت هر ESP
device_timestamp = {}

# تابع تعیین شماره ESP بر اساس code
def get_device_id(code):
    try:
        code = int(code)
        return code // 1000  # هر 1000 تا برای یک دستگاه
    except:
        return None


@app.route("/data", methods=["POST"])
def receive_data():
    """
    دریافت داده از ESP
    دیتا باید شامل فیلد 'code' باشد
    """
    global device_data, device_timestamp

    data = request.json

    if not data or "code" not in data:
        return jsonify({"error": "missing 'code' field"}), 400

    device_id = get_device_id(data["code"])
    if device_id is None:
        return jsonify({"error": "invalid code"}), 400

    # ذخیره در حافظه مخصوص همین ESP
    device_data[device_id] = data
    device_timestamp[device_id] = time.time()

    print(f"Device {device_id} updated:", data)

    return jsonify({"status": "success", "device_id": device_id})


@app.route("/poll", methods=["GET"])
def poll():
    """
    Long Polling – هر ESP فقط دیتای خودش را می‌گیرد
    نیازمند: ?device_id=0&last=12345
    """
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

        # اگر برای این دیوایس داده‌ای وجود دارد و جدید است
        if device_id in device_timestamp and device_timestamp[device_id] > last:
            return jsonify({
                "data": device_data[device_id],
                "timestamp": device_timestamp[device_id]
            })

        time.sleep(0.5)

    # بدون داده جدید
    return jsonify({"status": "no new data", "timestamp": last})


@app.route("/", methods=["GET"])
def home():
    """نمایش همه ESPها برای دیباگ"""
    return jsonify({
        "devices": device_data,
        "timestamps": device_timestamp
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
