from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    # نمایش IP سرور برای تست اینکه اینترنت کار می‌کند
    ip = requests.get("https://api.ipify.org").text
    html = f"""
    <html>
        <head><title>Proxy Status</title></head>
        <body>
            <h2>Render Server Proxy Status</h2>
            <p>Your public IP (via server): {ip}</p>
            <p>Server can reach the internet: {'Yes' if ip else 'No'}</p>
        </body>
    </html>
    """
    return html

@app.route('/fetch')
def fetch_url():
    # دریافت url از کامپیوتر
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url parameter missing"}), 400
    try:
        r = requests.get(url, timeout=15)
        return jsonify({
            "status_code": r.status_code,
            "headers": dict(r.headers),
            "body_b64": r.content.encode("base64").decode("utf-8") if r.content else ""
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
