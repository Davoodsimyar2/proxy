from flask import Flask, request, jsonify

app = Flask(__name__)

from flask import Flask, request, jsonify

app = Flask(__name__)

# یک متغیر ساده برای نگه‌داری آخرین داده دریافتی
last_data = {}

@app.route("/data", methods=["POST"])
def receive_data():
    global last_data
    last_data = request.json  # ذخیره کردن داده ارسالی
    print("Received data:", last_data)
    return jsonify({"status": "success", "received": last_data})

@app.route("/", methods=["GET"])
def home():
    if last_data:
        return f"""
        <h2>آخرین داده دریافتی:</h2>
        <pre>{last_data}</pre>
        """
    else:
        return "<h3>هنوز هیچ داده‌ای دریافت نشده است.</h3>"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

