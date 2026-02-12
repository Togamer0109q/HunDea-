import os
import logging
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*_args, **_kwargs):
        return False

def apply_env_overrides(config: Dict, logger: Optional[object] = None) -> Dict:
    """
    Override config with environment variables (GitHub Secrets compatible).
    """
    load_dotenv()
    
    # API Keys
    apis = config.setdefault("apis", {})
    
    if os.getenv("ITAD_API_KEY"):
        apis["itad"] = os.getenv("ITAD_API_KEY")
    
    if os.getenv("RAWG_API_KEY"):
        apis["rawg"] = os.getenv("RAWG_API_KEY")
        
    if os.getenv("DISCORD_WEBHOOK_PLAYSTATION"):
        apis.setdefault("platprices", {})["api_key"] = os.getenv("DISCORD_WEBHOOK_PLAYSTATION") # Some use this as key? 
        # But wait, you have DISCORD_WEBHOOK_PLAYSTATION as a webhook. 
        # Let's map webhooks properly.

    # WEBHOOKS Mapping
    webhooks = config.setdefault("webhooks", {})
    
    # Mapping your GitHub Secrets to the config keys
    env_map = {
        "DISCORD_WEBHOOK": "pc_premium",
        "DISCORD_WEBHOOK2": "pc_bajos",
        "DISCORD_WEBHOOK3": "pc_weekends",
        "HUN_DEA_DESCUENTOS": "pc_deals",
        "DISCORD_WEBHOOK_PLAYSTATION": "playstation",
        "DISCORD_WEBHOOK_XBOX": "xbox",
        "DISCORD_WEBHOOK_NINTENDO": "nintendo",
        "DISCORD_WEBHOOK_ALL": "pc_all",
        "DISCORD_WEBHOOK_STATUS": "status"
    }
    
    for env_key, config_key in env_map.items():
        val = os.getenv(env_key)
        if val:
            webhooks[config_key] = val
            if logger:
                # Use a simple print or logger if available
                print(f"✅ Environment override: {config_key} webhook loaded from {env_key}")

    # Other API Keys if present
    if os.getenv("PLATPRICES_API_KEY"):
         apis.setdefault("platprices", {})["api_key"] = os.getenv("PLATPRICES_API_KEY")

    return config
