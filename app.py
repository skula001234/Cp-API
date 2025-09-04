import os
import logging
import traceback
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

from utils.decoder import ClassPlusDecoder
from utils.classplus_client import ClassPlusClient
from utils.token_manager import generate_new_token
from utils.drm_manager import extract_keys_from_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Configure Flask-Limiter with Redis-like storage (fallback to memory)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Explicitly set memory storage
)
limiter.init_app(app)

decoder = ClassPlusDecoder()
classplus_client = ClassPlusClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player')
@limiter.limit("30 per minute")
def player():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing url query parameter"}), 400
    return render_template('player.html', url=url)

@app.route('/api/decode', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def decode_video_url():
    try:
        if request.method == 'GET':
            token = request.args.get('token')
            # accept both url and encrypted_url for compatibility
            encrypted_url = request.args.get('url') or request.args.get('encrypted_url')
        else:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400
            token = data.get('token')
            # accept both encrypted_url and url for flexibility
            encrypted_url = data.get('encrypted_url') or data.get('url')

        if not token or not encrypted_url:
            return jsonify({"error": "Token and encrypted_url/url are required"}), 400

        new_token_info = None
        if not classplus_client.validate_token(token):
            logger.warning(f"Token validation failed. Attempting to generate a new one.")
            token_result = generate_new_token()
            if token_result.get("success"):
                token = token_result["token"]
                new_token_info = {"token": token, "generated_by": token_result.get("email_used")}
                logger.info(f"Successfully generated a new token using {new_token_info['generated_by']}.")
            else:
                logger.error(f"Failed to auto-generate new token: {token_result.get('error')}")
                return jsonify({"error": "Token is invalid and auto-generation failed.", "details": token_result.get('error')}), 401
        
        decoded_url = decoder.decode_url(encrypted_url, token)
        if not decoded_url:
            return jsonify({"error": "Failed to decode URL"}), 400
        
        playable_url = decoder.generate_playable_url(decoded_url, token)
        
        response = {"status": "ok", "success": True, "url": playable_url}
        
        if new_token_info:
            response["new_token_info"] = new_token_info
            response["message"] = "Your old token was expired. A new token has been generated and used."

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in decode_video_url: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/get-keys', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def get_keys_api():
    try:
        if request.method == 'GET':
            token = request.args.get('token')
            # accept both url and video_url for compatibility
            video_url = request.args.get('url') or request.args.get('video_url')
        else:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            token = data.get('token')
            # accept both video_url and url
            video_url = data.get('video_url') or data.get('url')

        if not token or not video_url:
            return jsonify({"success": False, "error": "Token and video_url/url are required"}), 400
        
        if not classplus_client.validate_token(token):
            return jsonify({"success": False, "error": "Token is invalid or expired. Please use the decoder to get a new one."}), 401
            
        logger.info(f"Attempting to extract DRM keys for: {video_url}")
        result = extract_keys_from_url(video_url, token)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_keys_api: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error", "details": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(traceback.format_exc())
    
    response = {
        "success": False,
        "error": "Internal Server Error",
        "details": "An unexpected error occurred on the server. Please check the server logs for more information."
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
