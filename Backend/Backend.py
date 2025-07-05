import uuid
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from logger import LoggingMiddleware, log_function

app = Flask(__name__)
CORS(app)

logging_middleware = LoggingMiddleware(app)

url_mapping = {}

@app.route('/shorten', methods=['POST'])
@log_function
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    long_url = data.get('url')
    custom_code = data.get('shortcode')
    validity_minutes = data.get('validityInMinutes', 30)  
    
    try:
        validity_minutes = int(validity_minutes)
    except (ValueError, TypeError):
        return jsonify({"error": "Validity must be an integer"}), 400
    
    if custom_code:
        if not custom_code.isalnum() or len(custom_code) > 10:
            return jsonify({"error": "Invalid shortcode format"}), 400
        
        if custom_code in url_mapping and time.time() < url_mapping[custom_code]['expires_at']:
            return jsonify({"error": "Shortcode already in use"}), 409
        
        shortcode = custom_code
    else:
        while True:
            shortcode = str(uuid.uuid4())[:6]  
            if shortcode not in url_mapping or time.time() >= url_mapping[shortcode]['expires_at']:
                break
    
    expires_at = time.time() + (validity_minutes * 60)
    
    url_mapping[shortcode] = {
        "url": long_url,
        "expires_at": expires_at
    }
    
    short_url = f"http://localhost:5000/{shortcode}"
    return jsonify({
        "shortlink": short_url,
        "shortcode": shortcode,
        "expires_at": datetime.fromtimestamp(expires_at).isoformat()
    }), 201

@app.route('/<shortcode>', methods=['GET'])
@log_function
def redirect_url(shortcode):
    if shortcode not in url_mapping:
        return jsonify({"error": "Shortcode not found"}), 404
    
    if time.time() >= url_mapping[shortcode]['expires_at']:
        return jsonify({"error": "Link has expired"}), 410  
    
    return redirect(url_mapping[shortcode]['url'])

@app.route('/info/<shortcode>', methods=['GET'])
@log_function
def get_url_info(shortcode):
    if shortcode not in url_mapping:
        return jsonify({"error": "Shortcode not found"}), 404
    
    url_info = url_mapping[shortcode]
    
    is_expired = time.time() >= url_info['expires_at']
    
    return jsonify({
        "shortcode": shortcode,
        "url": url_info['url'],
        "expires_at": datetime.fromtimestamp(url_info['expires_at']).isoformat(),
        "is_expired": is_expired
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
