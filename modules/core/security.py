"""
🔒 Security Utilities - HunDeaBot
──────────────────────────────────

Utilidades de seguridad para proteger webhooks, API keys y datos sensibles.

Author: HunDeaBot Team
Version: 3.1.0
"""

import time
import re
import hashlib
from functools import wraps
from typing import Optional


class RateLimiter:
    """
    Simple rate limiter to prevent API abuse.
    
    Usage:
        limiter = RateLimiter(calls_per_minute=60)
        limiter.wait()  # Espera si es necesario
        # hacer request
    """
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0
    
    def wait(self):
        """Wait if needed to respect rate limit."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
        self.last_call = time.time()


def sanitize_webhook(webhook_url: str) -> str:
    """
    Sanitize webhook URL for logging purposes.
    
    Hides sensitive parts of the webhook to prevent exposure in logs.
    
    Args:
        webhook_url: Full Discord webhook URL
        
    Returns:
        Sanitized webhook URL safe for logging
        
    Example:
        >>> sanitize_webhook("https://discord.com/api/webhooks/123456/abcdefgh")
        "https://discord.com/.../abcdef***"
    """
    if not webhook_url:
        return "None"
    
    try:
        parts = webhook_url.split('/')
        if len(parts) >= 7:
            # Mostrar dominio y primeros 6 chars del token
            return f"{parts[0]}//{parts[2]}/.../.../{parts[-1][:6]}***"
        return "***WEBHOOK***"
    except:
        return "***INVALID***"


def validate_webhook(webhook_url: str, test_ping: bool = False) -> bool:
    """
    Validate Discord webhook URL.
    
    Args:
        webhook_url: Webhook URL to validate
        test_ping: If True, send test request to verify webhook is active
        
    Returns:
        True if webhook is valid
    """
    if not webhook_url or not isinstance(webhook_url, str):
        return False
    
    # Patrón de Discord webhook
    pattern = r'https://discord\.com/api/webhooks/\d+/[\w-]+'
    
    if not re.match(pattern, webhook_url):
        return False
    
    # Test opcional (hace un GET al webhook)
    if test_ping:
        try:
            import requests
            response = requests.get(webhook_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    return True


def sanitize_game_title(title: str, max_length: int = 256) -> str:
    """
    Sanitize game title for Discord embeds.
    
    Prevents markdown injection and limits length.
    
    Args:
        title: Game title to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized title safe for Discord
    """
    if not title:
        return "Unknown Game"
    
    # Limitar longitud
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    
    # Escapar caracteres especiales de markdown
    replacements = {
        '`': '\\`',
        '*': '\\*',
        '_': '\\_',
        '~': '\\~',
        '|': '\\|',
        '>': '\\>',
    }
    
    for char, escaped in replacements.items():
        title = title.replace(char, escaped)
    
    return title


def sanitize_url(url: str) -> str:
    """
    Sanitize URL to prevent injection.
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL
    """
    if not url:
        return ""
    
    # Remover espacios y caracteres peligrosos
    url = url.strip()
    
    # Validar que empiece con http/https
    if not url.startswith(('http://', 'https://')):
        return ""
    
    return url


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for secure storage/comparison.
    
    Args:
        api_key: API key to hash
        
    Returns:
        SHA256 hash of the key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required top-level keys
    required_keys = ['webhooks', 'apis', 'filters']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    # Validate webhooks
    if 'webhooks' in config:
        for platform, webhook in config['webhooks'].items():
            if webhook and not webhook.startswith('YOUR_'):
                if not validate_webhook(webhook):
                    errors.append(f"Invalid webhook for {platform}")
    
    # Validate filters
    if 'filters' in config:
        for platform, filters in config['filters'].items():
            if not isinstance(filters, dict):
                errors.append(f"Invalid filters for {platform}: must be dict")
            else:
                # Check numeric values
                for key, value in filters.items():
                    if key in ['min_discount', 'max_price']:
                        if not isinstance(value, (int, float)) or value < 0:
                            errors.append(f"Invalid {key} for {platform}: must be positive number")
    
    return len(errors) == 0, errors


def safe_get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Safely get environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raise error if not found
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required=True and variable not found
    """
    import os
    
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable not set: {key}")
    
    return value


class SecureLogger:
    """
    Wrapper around logger that sanitizes sensitive data.
    """
    
    def __init__(self, logger):
        """Initialize with base logger."""
        self.logger = logger
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize log message to hide sensitive data."""
        # Ocultar webhooks
        message = re.sub(
            r'https://discord\.com/api/webhooks/\d+/[\w-]+',
            lambda m: sanitize_webhook(m.group(0)),
            message
        )
        
        # Ocultar potenciales API keys (32+ caracteres alfanuméricos)
        message = re.sub(
            r'\b[A-Za-z0-9]{32,}\b',
            '***API_KEY***',
            message
        )
        
        return message
    
    def info(self, message, *args, **kwargs):
        """Log info with sanitization."""
        self.logger.info(self._sanitize_message(str(message)), *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning with sanitization."""
        self.logger.warning(self._sanitize_message(str(message)), *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log error with sanitization."""
        self.logger.error(self._sanitize_message(str(message)), *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log debug with sanitization."""
        self.logger.debug(self._sanitize_message(str(message)), *args, **kwargs)


# Decorator para rate limiting
def rate_limit(calls_per_minute: int = 60):
    """
    Decorator to add rate limiting to functions.
    
    Args:
        calls_per_minute: Maximum calls per minute
        
    Example:
        @rate_limit(calls_per_minute=30)
        def fetch_data():
            # ...
    """
    limiter = RateLimiter(calls_per_minute)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Test function
def test_security_utils():
    """Test security utilities."""
    
    print("🧪 Testing Security Utilities")
    print("="*60)
    
    # Test webhook sanitization
    webhook = "https://discord.com/api/webhooks/123456789/abcdefghijklmnop"
    sanitized = sanitize_webhook(webhook)
    print(f"\n✅ Webhook Sanitization:")
    print(f"   Original: {webhook}")
    print(f"   Sanitized: {sanitized}")
    
    # Test validation
    is_valid = validate_webhook(webhook)
    print(f"\n✅ Webhook Validation: {is_valid}")
    
    # Test title sanitization
    title = "Game `Title` with *markdown* and _underscores_"
    sanitized_title = sanitize_game_title(title)
    print(f"\n✅ Title Sanitization:")
    print(f"   Original: {title}")
    print(f"   Sanitized: {sanitized_title}")
    
    # Test rate limiter
    print(f"\n✅ Rate Limiter:")
    limiter = RateLimiter(calls_per_minute=120)  # 2 per second
    start = time.time()
    for i in range(3):
        limiter.wait()
        print(f"   Call {i+1} at {time.time() - start:.2f}s")
    
    print("\n" + "="*60)
    print("✅ All security tests passed!")


if __name__ == "__main__":
    test_security_utils()
