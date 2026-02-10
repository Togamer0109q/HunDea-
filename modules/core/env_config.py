import os
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False


def apply_env_overrides(config: Dict, logger: Optional[object] = None) -> Dict:
    """
    Load .env and override config with environment variables.
    Environment variables take priority over config.json.
    """
    load_dotenv()

    apis = config.setdefault("apis", {})

    rawg = os.getenv("RAWG_API_KEY")
    if rawg:
        apis["rawg"] = rawg

    itad = os.getenv("ITAD_API_KEY")
    if itad:
        apis["itad"] = itad

    ggdeals = os.getenv("GGDEALS_API_KEY")
    if ggdeals:
        apis["ggdeals"] = ggdeals

    ggdeals_region = os.getenv("GGDEALS_REGION")
    if ggdeals_region:
        apis["ggdeals_region"] = ggdeals_region.lower()

    platprices = os.getenv("PLATPRICES_API_KEY")
    if platprices:
        apis.setdefault("platprices", {})["api_key"] = platprices
        apis.setdefault("psprices", {})["api_key"] = platprices

    xbox_client_id = os.getenv("XBOX_CLIENT_ID")
    if xbox_client_id:
        apis.setdefault("xbox", {})["client_id"] = xbox_client_id

    xbox_client_secret = os.getenv("XBOX_CLIENT_SECRET")
    if xbox_client_secret:
        apis.setdefault("xbox", {})["client_secret"] = xbox_client_secret

    if logger:
        logger.debug("Environment overrides applied to config")

    return config
