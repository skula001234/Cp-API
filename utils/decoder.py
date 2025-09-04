import base64
import json
import logging
import hmac
import hashlib
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ClassPlusDecoder:

    def decode_url(self, encrypted_url, token):
        """Decode encrypted URL from base64 or return as-is if not encoded."""
        try:
            # Try to decode as base64
            decoded_bytes = base64.b64decode(encrypted_url.encode('utf-8'))
            return decoded_bytes.decode('utf-8')
        except Exception:
            # If not base64, return original URL
            return encrypted_url

    def generate_playable_url(self, decoded_url, token):
        """Generate a secure, playable URL with HMAC signature."""
        try:
            logger.info(f"Generating secure URL for: {decoded_url}")
            
            # Extract user_id from JWT token
            user_id = self._extract_user_id_from_token(token)
            if not user_id:
                logger.error("Could not extract user_id from token.")
                return decoded_url  # Fallback if user_id not found

            parsed_url = urlparse(decoded_url)
            base_url_path = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            # Create correct URL prefix for signing
            path_parts = parsed_url.path.strip('/').split('/')
            if path_parts and '.' in path_parts[-1]:  # If last part is a file
                path_prefix = '/'.join(path_parts[:-1])
            else:
                path_prefix = parsed_url.path.strip('/')

            url_prefix_for_signing = f"{parsed_url.scheme}://{parsed_url.netloc}/{path_prefix}"
            
            expiry_time = int(time.time()) + 3600  # 1 hour expiry

            # This is the most important part
            # "Unsigned request rejected" means HMAC signature is wrong,
            # usually due to incorrect Secret Key.
            # For proper solution, extract real Secret Key from the app.
            hmac_secret = b"classplus_-$-video_encryption_--$-key"  # This is an estimated key

            url_prefix_b64 = base64.b64encode(url_prefix_for_signing.encode()).decode().rstrip("=")
            
            data_to_sign = f"URLPrefix={url_prefix_b64}~Expires={expiry_time}"
            
            signature = hmac.new(
                hmac_secret,
                data_to_sign.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            hdnts_param = f"URLPrefix={url_prefix_b64}~Expires={expiry_time}~hmac={signature}"
            
            # Create final secure URL
            final_url = f"{base_url_path}?hdnts={hdnts_param}&userIds={user_id}"
            logger.info(f"Generated secure URL with estimated key: {final_url}")
            
            return final_url

        except Exception as e:
            logger.error(f"Error generating playable URL: {e}", exc_info=True)
            return decoded_url  # Fallback on any error

    def _extract_user_id_from_token(self, token):
        """Extract user ID from JWT token."""
        try:
            parts = token.split('.')
            if len(parts) < 2: 
                return None
            
            payload_b64 = parts[1]
            payload_b64 += '=' * (-len(payload_b64) % 4)  # Add padding
            
            payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
            return str(payload.get('id'))
        except Exception as e:
            logger.error(f"Could not extract user ID from token: {e}")
            return None

