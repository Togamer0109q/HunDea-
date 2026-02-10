"""
🟦 PlayStation Hunter - FIXED with REAL PlatPrices API
──────────────────────────────────────────────────────

Uses the CORRECT PlatPrices API endpoints based on official documentation:
https://platprices.com/developers.php

Author: HunDeaBot Team
Version: 3.9.0 - REAL API FIXED
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
    PlayStation hunter with CORRECT PlatPrices API.
    """
    
    # CORRECT API endpoint
    API_URL = "https://platprices.com/api.php"
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """Initialize PlayStation hunter."""
        super().__init__(config, cache_manager, logger)
        
        # Get API key
        ps_config = config.get('apis', {}).get('platprices', {})
        self.api_key = ps_config.get('api_key') or config.get('apis', {}).get('psprices', {}).get('api_key')
        if not self.api_key:
            load_dotenv()
            self.api_key = os.getenv('PLATPRICES_API_KEY')
        self.region = ps_config.get('region', 'us').lower()
        
        if self.api_key:
            self.logger.info(f"🟦 PlayStation Hunter initialized with API key")
            self.logger.info(f"🔑 API Key: {self.api_key[:20]}...")
            self.logger.info(f"🌍 Region: {self.region.upper()}")
        else:
            self.logger.warning("⚠️  No PlatPrices API key!")
    
    def get_platform_name(self) -> str:
        return "PlayStation"
    
    def fetch_deals(self) -> List[ConsoleDeal]:
        """Fetch PlayStation deals using CORRECT API."""
        deals = []
        
        if not self.api_key:
            self.logger.error("❌ No API key")
            return deals
        
        try:
            self.logger.info("🔍 Fetching from PlatPrices API (REAL endpoint)...")
            
            # CORRECT parameters according to docs
            params = {
                'key': self.api_key,
                'discount': '1'  # Get all games with new discounts (last 48h)
            }
            
            headers = {
                'User-Agent': 'HunDeaBot/3.9.0'
            }
            
            self.logger.debug(f"URL: {self.API_URL}")
            self.logger.debug(f"Params: discount=1")
            
            response = requests.get(
                self.API_URL,
                params=params,
                headers=headers,
                timeout=30
            )
            
            # Check response
            if response.status_code != 200:
                self.logger.warning(f"⚠️  Status {response.status_code}")
                self.logger.debug(f"Response: {response.text[:200]}")
                return deals
            
            # Parse JSON response
            data = response.json()
            
            # According to docs, response should be array of products
            if isinstance(data, dict):
                # Check for error
                if data.get('error', 0) != 0:
                    self.logger.error(f"❌ API error: {data.get('error')}")
                    return deals
                
                # Might be wrapped in a key
                products = data.get('products') or data.get('games') or []
            elif isinstance(data, list):
                products = data
            else:
                self.logger.warning("⚠️  Unexpected response format")
                return deals
            
            self.logger.info(f"📥 Received {len(products)} PlayStation deals")
            
            # Parse each deal
            for item in products:
                deal = self._parse_platprices_deal(item)
                if deal:
                    deals.append(deal)
            
            self.logger.info(f"✅ Parsed {len(deals)} valid deals")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request error: {e}")
        except ValueError as e:
            self.logger.error(f"❌ JSON parse error: {e}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
        
        return deals
    
    def _parse_platprices_deal(self, item: Dict) -> Optional[ConsoleDeal]:
        """
        Parse deal from PlatPrices API response.
        
        According to docs, fields include:
        - ProductName, GameName
        - CurrentPrice, BasePrice
        - PercentOff
        - PlatPricesURL, PSStoreURL
        - Publisher, Developer
        - MetacriticScore, OpenCriticID
        - Platforms (array)
        """
        try:
            # Title
            title = item.get('ProductName') or item.get('GameName') or 'Unknown'
            
            # Prices - PlatPrices uses cents
            current_price_cents = item.get('CurrentPrice', 0)
            base_price_cents = item.get('BasePrice', 0) or current_price_cents
            
            # Convert cents to dollars
            current_price = float(current_price_cents) / 100 if current_price_cents else 0.0
            base_price = float(base_price_cents) / 100 if base_price_cents else current_price
            
            # Discount
            discount = item.get('PercentOff', 0)
            if not discount and base_price > current_price > 0:
                discount = int(((base_price - current_price) / base_price) * 100)
            
            # Skip if no discount
            if discount == 0:
                return None
            
            # URLs
            store_url = item.get('PSStoreURL') or item.get('PlatPricesURL') or ''
            
            # Platform
            platforms = item.get('Platforms', [])
            if isinstance(platforms, list) and platforms:
                console_gen = 'PS5' if 'PS5' in str(platforms) else 'PS4'
            else:
                console_gen = 'PS5'
            
            # Game ID
            game_id = item.get('PPID') or item.get('PSNID') or title.replace(' ', '_')[:50]
            
            # Create deal
            deal = ConsoleDeal(
                title=title,
                store_url=store_url,
                platform="PlayStation",
                console_gen=console_gen,
                
                original_price=base_price,
                current_price=current_price,
                discount_percent=int(discount),
                currency="USD",
                
                game_id=f"ps_{game_id}",
                publisher=item.get('Publisher'),
                developer=item.get('Developer'),
                
                metacritic_score=item.get('MetacriticScore'),
                
                is_dlc=self._is_dlc(title)
            )
            
            return deal
            
        except Exception as e:
            self.logger.debug(f"Parse error: {e}")
            return None
    
    def _is_dlc(self, title: str) -> bool:
        """Check if DLC."""
        dlc_keywords = [
            'dlc', 'add-on', 'addon', 'expansion', 'season pass',
            'bundle', 'pack', 'edition upgrade', 'content pack'
        ]
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in dlc_keywords)
    
    def get_game_details(self, game_id: str) -> Optional[Dict]:
        """Get game details - Required by base class."""
        return None


# Test
def test_playstation():
    """Test with REAL API."""
    
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    print("\n" + "="*60)
    print("🟦 PLAYSTATION HUNTER TEST - REAL API")
    print("="*60)
    
    config = {
        'apis': {
            'platprices': {
                'api_key': 'GH28jbaLCoVsQ5QINHnV8fHpvsQnuUbB',
                'region': 'us'
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
    
    class MockCache:
        def is_posted(self, game_id):
            return False
        def add_to_cache(self, game_id, data):
            pass
    
    cache = MockCache()
    hunter = PlayStationHunter(config, cache, logger)
    
    print("\n🔍 Fetching deals...")
    deals = hunter.fetch_deals()
    
    print(f"\n📊 RESULTS:")
    print("="*60)
    print(f"Total deals: {len(deals)}")
    
    if deals:
        print(f"\n🎮 First 10 Deals:")
        print("-"*60)
        
        for i, deal in enumerate(deals[:10], 1):
            print(f"\n{i}. {deal.title}")
            print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
            print(f"   📊 {deal.discount_percent}% OFF")
            print(f"   🎮 {deal.console_gen}")
    else:
        print("\n❌ NO DEALS FOUND")
        print("\nPossible issues:")
        print("1. API key invalid")
        print("2. No current sales")
        print("3. Rate limit exceeded (500/hour)")
    
    print("\n" + "="*60)
    
    return deals


if __name__ == "__main__":
    test_playstation()
