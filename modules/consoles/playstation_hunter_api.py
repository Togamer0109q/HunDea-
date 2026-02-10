"""
🟦 PlayStation Hunter - PlatPrices API Edition
───────────────────────────────────────────────

NOW WITH REAL API KEY! 🎉

Uses PlatPrices.com API to fetch PlayStation deals.
API Key: Configured in config.json

Author: HunDeaBot Team
Version: 3.6.0 - API KEY EDITION
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False
from .base_console_hunter import BaseConsoleHunter, ConsoleDeal


class PlayStationHunter(BaseConsoleHunter):
    """
    PlayStation hunter with REAL PlatPrices API.
    """
    
    # PlatPrices API Endpoint (from developers.php)
    BASE_URL = "https://platprices.com/api.php"
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """Initialize PlayStation hunter."""
        super().__init__(config, cache_manager, logger)
        
        # Get API key from config
        ps_config = config.get('apis', {}).get('platprices', {})
        self.api_key = ps_config.get('api_key') or config.get('apis', {}).get('psprices', {}).get('api_key')
        if not self.api_key:
            load_dotenv()
            self.api_key = os.getenv('PLATPRICES_API_KEY')
        self.region = ps_config.get('region', 'us').lower()
        self.platform = ps_config.get('platform', 'ps5').lower()
        
        if not self.api_key:
            self.logger.warning("⚠️  No PlatPrices API key found!")
            self.logger.info("💡 Run: python setup_platprices.py")
        else:
            self.logger.info(f"🟦 PlayStation Hunter initialized with API key")
            self.logger.info(f"🔑 API Key: {self.api_key[:20]}...")
            self.logger.info(f"🌍 Region: {self.region.upper()}")
    
    def get_platform_name(self) -> str:
        """Return platform name."""
        return "PlayStation"
    
    def fetch_deals(self) -> List[ConsoleDeal]:
        """
        Fetch PlayStation deals using PlatPrices API.
        Uses 'discount=1' to get recently discounted games.
        """
        deals = []
        
        if not self.api_key:
            self.logger.error("❌ No API key - cannot fetch deals")
            return deals
        
        try:
            params = {
                'key': self.api_key,
                'region': self.region,
                'discount': '1'  # Get recently discounted games
            }
            
            headers = {
                'User-Agent': 'HunDeaBot/3.6.0',
                'Accept': 'application/json'
            }
            
            self.logger.info(f"🔍 Fetching from PlatPrices API...")
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.logger.error(f"❌ API Error: Status {response.status_code}")
                return deals
            
            data = response.json()
            
            # Check for API error (API returns error field)
            if isinstance(data, dict) and data.get('error', 0) != 0:
                self.logger.error(f"❌ PlatPrices API Error: {data.get('errorDesc', 'Unknown error')}")
                return deals
            
            # Get deals list - The API returns a dictionary with a 'discounts' key
            if isinstance(data, dict):
                results = data.get('discounts', [])
            else:
                self.logger.error("❌ Unexpected API response format")
                return deals

            self.logger.info(f"📥 Received {len(results)} PlayStation deals")
            
            # Parse each deal
            for item in results:
                deal = self._parse_deal(item)
                if deal:
                    deals.append(deal)
            
            self.logger.info(f"✅ Parsed {len(deals)} valid deals")
            
        except Exception as e:
            self.logger.error(f"❌ PlatPrices API error: {e}")
        
        return deals
    
    def get_game_details(self, game_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific game using 'ppid'.
        """
        if not self.api_key:
            return None

        # Extract PPID from game_id (format: "ps_12345")
        ppid = game_id.replace('ps_', '') if game_id.startswith('ps_') else game_id
        
        try:
            params = {
                'key': self.api_key,
                'ppid': ppid,
                'region': self.region
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            data = response.json()
            
            if data.get('error', 0) == 0:
                return data
                
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to fetch details for {game_id}: {e}")
            
        return None

    def _parse_deal(self, item: Dict) -> Optional[ConsoleDeal]:
        """
        Parse deal from PlatPrices 'discounts' list.
        Prices are in cents (e.g., 8999 -> 89.99).
        """
        try:
            # Get title
            title = item.get('Name', 'Unknown Game')
            
            # Get prices (convert from cents)
            try:
                sale_price = float(item.get('SalePrice', 0)) / 100.0
                regular_price = float(item.get('BasePrice', 0)) / 100.0
                # PlusPrice is also available if needed
            except (ValueError, TypeError):
                return None
            
            # Skip if no regular price or invalid data
            if regular_price <= 0:
                return None
            
            # Calculate discount
            discount = 0
            if regular_price > 0:
                # Use float division and round to nearest integer
                discount = int(round(((regular_price - sale_price) / regular_price) * 100))
            
            # Helper for ID
            ppid = item.get('PPID')
            if not ppid:
                return None
            
            # Get URL
            url = item.get('PlatPricesURL') or f"https://platprices.com/game/{ppid}"
            
            # Create deal
            deal = ConsoleDeal(
                title=title,
                store_url=url,
                platform="PlayStation",
                console_gen="PS4/PS5", # PlatPrices often mixes, assume generic
                
                original_price=regular_price,
                current_price=sale_price,
                discount_percent=discount,
                currency="USD", # Default to USD as per docs examples
                
                game_id=f"ps_{ppid}",
                
                # Metacritic/User score not in list response, requires detail fetch
                # Will be enriched later via enrich_deal if needed
                
                is_dlc=self._is_dlc(title)
            )
            
            return deal
            
        except Exception as e:
            self.logger.debug(f"Error parsing deal: {e}")
            return None
    
    def _is_dlc(self, title: str) -> bool:
        """Check if title is DLC."""
        dlc_keywords = [
            'dlc', 'add-on', 'addon', 'expansion', 'season pass',
            'bundle', 'pack', 'edition upgrade', 'content pack'
        ]
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in dlc_keywords)


# Test function
def test_playstation():
    """Test PlayStation hunter with real API key."""
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🟦 PLAYSTATION HUNTER TEST (WITH API KEY)")
    print("="*60)
    
    # Config with API key
    config = {
        'apis': {
            'platprices': {
                'api_key': 'GH28jbaLCoVsQ5QINHnV8fHpvsQnuUbB',
                'region': 'us',
                'platform': 'ps5'
            }
        },
        'filters': {
            'playstation': {
                'min_discount': 0,
                'min_score': 0,
                'exclude_dlc': False,
                'max_price': 999999
            }
        }
    }
    
    # Mock cache
    class MockCache:
        def is_posted(self, game_id):
            return False
        def add_to_cache(self, game_id, data):
            pass
    
    cache = MockCache()
    
    # Create hunter
    hunter = PlayStationHunter(config, cache)
    
    # Fetch deals
    print("\n🔍 Fetching PlayStation deals...")
    deals = hunter.fetch_deals()
    
    print(f"\n📊 RESULTS:")
    print(f"{'='*60}")
    print(f"Total deals found: {len(deals)}")
    
    if deals:
        print(f"\n🎮 Sample Deals:")
        print("-"*60)
        
        for i, deal in enumerate(deals[:10], 1):
            print(f"\n{i}. {deal.title}")
            print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
            print(f"   📊 {deal.discount_percent}% OFF")
            print(f"   🎮 {deal.console_gen}")
    else:
        print("\n⚠️  No deals found")
        print("💡 Check API key or try different region/platform")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_playstation()
