import logging
import os
from typing import Dict, List, Optional

import requests

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False


class GGDealsHunter:
    """
    GG.deals API hunter.
    - Active bundles (no Steam IDs required)
    - Price lookup by Steam App ID (optional utility)
    """

    BASE_URL = "https://api.gg.deals/v1"

    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None, logger=None):
        load_dotenv()
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("GGDEALS_API_KEY")
        self.region = (region or os.getenv("GGDEALS_REGION") or "us").lower()

        if not self.api_key:
            self.logger.warning("GG.deals API key missing (set GGDEALS_API_KEY in .env)")

    def fetch_deals(self) -> List[Dict]:
        """Return active bundle deals."""
        return self.fetch_active_bundles()

    def fetch_active_bundles(self, max_pages: int = 1) -> List[Dict]:
        if not self.api_key:
            return []

        url = f"{self.BASE_URL}/bundles/active/"
        params = {"key": self.api_key, "region": self.region}

        deals: List[Dict] = []
        next_url = url
        pages = 0

        while next_url and pages < max_pages:
            try:
                if next_url == url:
                    response = requests.get(next_url, params=params, timeout=30)
                else:
                    response = requests.get(next_url, timeout=30)
                response.raise_for_status()
            except Exception as exc:
                self.logger.error("GG.deals bundles request failed: %s", exc)
                break

            payload = response.json()
            if not payload.get("success", True):
                self.logger.warning("GG.deals bundles response has success=false")
                break

            data = payload.get("data", {})
            bundles = data.get("bundles", []) or []

            for bundle in bundles:
                deal = self._parse_bundle(bundle)
                if deal:
                    deals.append(deal)

            next_url = data.get("next")
            pages += 1

        self.logger.info("GG.deals bundles fetched: %s", len(deals))
        return deals

    def get_prices_by_steam_app_ids(self, steam_app_ids: List[str], region: Optional[str] = None) -> Dict[str, Dict]:
        """
        Price lookup for up to 100 Steam App IDs per request.
        Returns a dict keyed by app id with GG.deals price data.
        """
        if not self.api_key:
            return {}

        if not steam_app_ids:
            return {}

        region = (region or self.region or "us").lower()
        results: Dict[str, Dict] = {}

        # Chunk to 100 IDs per request
        for i in range(0, len(steam_app_ids), 100):
            chunk = steam_app_ids[i : i + 100]
            params = {
                "key": self.api_key,
                "ids": ",".join(str(x) for x in chunk),
                "region": region,
            }

            try:
                response = requests.get(
                    f"{self.BASE_URL}/prices/by-steam-app-id/",
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
            except Exception as exc:
                self.logger.error("GG.deals prices request failed: %s", exc)
                continue

            payload = response.json()
            if not payload.get("success", True):
                self.logger.warning("GG.deals prices response has success=false")
                continue

            data = payload.get("data", {})
            for app_id, info in data.items():
                if info:
                    results[str(app_id)] = info

        return results

    def _parse_bundle(self, bundle: Dict) -> Optional[Dict]:
        title = bundle.get("title") or "Unknown bundle"
        url = bundle.get("url")
        date_from = bundle.get("dateFrom")
        date_to = bundle.get("dateTo")

        tiers = bundle.get("tiers", []) or []
        min_price = None
        currency = None

        for tier in tiers:
            price_str = tier.get("price")
            currency = tier.get("currency") or currency
            try:
                price_val = float(price_str) if price_str is not None else None
            except (TypeError, ValueError):
                price_val = None
            if price_val is not None:
                min_price = price_val if min_price is None else min(min_price, price_val)

        return {
            "title": title,
            "url": url,
            "price": min_price,
            "currency": currency,
            "start_date": date_from,
            "end_date": date_to,
            "type": "bundle",
            "source": "ggdeals",
        }
