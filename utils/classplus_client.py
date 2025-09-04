import logging
import requests
import time

logger = logging.getLogger(__name__)

class ClassPlusClient:
    """Handles communication with the ClassPlus API for token validation."""
    def __init__(self):
        self.base_url = "https://api.classplusapp.com"
        self.timeout = 5
        self.token_cache = {}
        self.cache_duration = 300  # 5 minutes

    def validate_token(self, token):
        """Validates a ClassPlus authentication token."""
        try:
            # Check cache first to avoid unnecessary API calls
            if token in self.token_cache and (time.time() - self.token_cache[token]['timestamp'] < self.cache_duration):
                return self.token_cache[token]['valid']

            headers = {'x-access-token': token}
            # Use a lightweight endpoint for validation
            response = requests.get(f"{self.base_url}/v2/users/details", headers=headers, timeout=self.timeout)
            is_valid = response.status_code == 200
            
            self.token_cache[token] = {'valid': is_valid, 'timestamp': time.time()}
            logger.info(f"Token validation result: {'VALID' if is_valid else 'INVALID'}")
            return is_valid
        except requests.exceptions.RequestException:
            # If the API call fails, assume the token might be valid to allow an attempt.
            logger.warning("Token validation API call failed. Assuming token might be valid.")
            return True
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            return False
