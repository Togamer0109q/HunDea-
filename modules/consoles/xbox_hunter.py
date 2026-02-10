"""
🟩 Xbox Hunter - Microsoft Store API Integration
─────────────────────────────────────────────────

Fetches Xbox Store deals using Microsoft's public APIs.
Supports Xbox One, Xbox Series X|S, and Game Pass.

API Documentation: https://docs.microsoft.com/en-us/gaming/
Rate Limits: Generous (no key required for public endpoints)

Author: HunDeaBot Team
Version: 3.0.0
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .base_console_hunter import BaseConsoleHunter, ConsoleDeal


class XboxHunter(BaseConsoleHunter):
    """
    Xbox-specific deal hunter using Microsoft's Recommendation API (Reliable).
    """
    
    # More reliable Xbox Deals endpoint (used by Xbox.com)
    RECO_URL = "https://reco-public.rec.mp.microsoft.com/channels/XboxMarketplace/Deals"
    CATALOG_URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"
    BASE_URL = CATALOG_URL # Compatibility
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """Initialize Xbox hunter."""
        super().__init__(config, cache_manager, logger)
        
        # Xbox-specific config
        xbox_config = config.get('apis', {}).get('xbox', {})
        self.market = xbox_config.get('region', 'us').upper()
        self.language = xbox_config.get('language', 'en-US')
        self.include_game_pass = self.platform_config.get('include_game_pass', True)
        
        self.logger.info(f"🟩 Xbox Hunter configured (Reco API)")
        self.logger.info(f"🌍 Market: {self.market}, Language: {self.language}")
    
    def get_platform_name(self) -> str:
        """Return platform name."""
        return "Xbox"
    
    def fetch_deals(self) -> List[ConsoleDeal]:
        """
        Fetch current Xbox Store deals.
        """
        deals = []
        
        try:
            # 1. Try Recommendation API (Very reliable for sales)
            params = {
                'market': self.market,
                'languages': self.language,
                'count': 100
            }
            
            self.logger.debug(f"🔍 Fetching from Xbox Reco API...")
            
            # DNS Retry logic
            response = None
            for _ in range(2):
                try:
                    response = requests.get(self.RECO_URL, params=params, timeout=15)
                    response.raise_for_status()
                    break
                except Exception:
                    import time
                    time.sleep(2)
            
            if not response:
                raise Exception("Failed to resolve or connect to Xbox API")
            
            data = response.json()
            # This API returns a list of product IDs
            items = data.get('Items', [])
            product_ids = [item.get('Id') for item in items if item.get('Id')]
            
            if not product_ids:
                self.logger.warning("⚠️ No products found in Xbox Reco API")
            else:
                self.logger.info(f"📥 Found {len(product_ids)} Xbox product IDs")
                # Fetch details for these IDs in chunks of 20
                for i in range(0, len(product_ids), 20):
                    chunk = product_ids[i:i+20]
                    chunk_deals = self._fetch_product_details(chunk)
                    deals.extend(chunk_deals)
            
        except Exception as e:
            self.logger.warning(f"⚠️  Xbox Reco API failed: {e}")
            self.logger.info("🦈 Using CheapShark as fallback...")
            
            # Fallback to CheapShark (already implemented in modules.core)
            try:
                from modules.core.xbox_cheapshark import fetch_xbox_deals_cheapshark
                cheapshark_deals = fetch_xbox_deals_cheapshark(max_deals=100, logger=self.logger)
                
                for deal_data in cheapshark_deals:
                    deal = ConsoleDeal(
                        title=deal_data['name'],
                        store_url=deal_data.get('url', 'https://www.xbox.com'),
                        platform="Xbox",
                        console_gen="Xbox Series X|S",
                        original_price=deal_data['original_price'],
                        current_price=deal_data['current_price'],
                        discount_percent=deal_data['discount_percent'],
                        currency=deal_data.get('currency', 'USD'),
                        game_id=f"xbox_{deal_data.get('deal_id', deal_data['name'].replace(' ', '_'))}",
                        is_dlc=self._is_dlc(deal_data['name'])
                    )
                    deals.append(deal)
            except Exception as fb_err:
                self.logger.error(f"❌ Xbox fallback also failed: {fb_err}")
        
        return deals

    def _fetch_product_details(self, product_ids: List[str]) -> List[ConsoleDeal]:
        """Fetch full details for a list of Product IDs."""
        deals = []
        try:
            ids_str = ",".join(product_ids)
            url = f"{self.CATALOG_URL}?productIds={ids_str}&market={self.market}&languages={self.language}"
            
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            
            products = response.json().get('Products', [])
            for product in products:
                deal = self._parse_deal(product)
                if deal:
                    deals.append(deal)
        except Exception as e:
            self.logger.debug(f"Error fetching product details: {e}")
        return deals
    
    def _parse_deal(self, product: Dict) -> Optional[ConsoleDeal]:
        """
        Parse a single product from API response.
        
        Args:
            product: Raw product data from API
            
        Returns:
            ConsoleDeal object or None if invalid
        """
        try:
            # Get display properties
            properties = product.get('DisplaySkuAvailabilities', [{}])[0]
            availabilities = properties.get('Availabilities', [{}])[0]
            
            # Extract pricing
            order_management = availabilities.get('OrderManagementData', {})
            price_info = order_management.get('Price', {})
            
            # List price and sale price
            list_price = float(price_info.get('ListPrice', 0))
            msrp = float(price_info.get('MSRP', list_price))
            
            # Skip if no discount
            if list_price == 0 or list_price >= msrp:
                return None
            
            # Calculate discount
            discount_percent = int(((msrp - list_price) / msrp) * 100)
            
            # Get product info
            localized_props = product.get('LocalizedProperties', [{}])[0]
            title = localized_props.get('ProductTitle', 'Unknown Game')
            publisher = localized_props.get('PublisherName', '')
            developer = localized_props.get('DeveloperName', publisher)
            
            # Determine console generation
            platforms = product.get('Properties', {}).get('XboxPlatforms', [])
            console_gen = self._determine_console(platforms)
            
            # Check Game Pass availability
            is_game_pass = self._is_game_pass(product)
            
            # Get product ID
            product_id = product.get('ProductId', '')
            
            # Create deal object
            deal = ConsoleDeal(
                title=title,
                store_url=f"https://www.microsoft.com/en-{self.market}/p/{product_id}",
                platform="Xbox",
                console_gen=console_gen,
                
                original_price=msrp,
                current_price=list_price,
                discount_percent=discount_percent,
                currency=price_info.get('CurrencyCode', 'USD'),
                
                game_id=f"xbox_{product_id}",
                release_date=product.get('MarketProperties', [{}])[0].get('OriginalReleaseDate'),
                publisher=publisher,
                developer=developer,
                genre=self._extract_genre(product),
                
                is_game_pass=is_game_pass,
                is_dlc=self._is_dlc(title, product)
            )
            
            return deal
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to parse product: {e}")
            return None
    
    def _determine_console(self, platforms: List[str]) -> str:
        """Determine console generation from platforms list."""
        if 'XboxSeriesX' in platforms or 'Scarlett' in platforms:
            return 'Xbox Series X|S'
        elif 'XboxOne' in platforms:
            return 'Xbox One'
        elif 'PC' in platforms:
            return 'PC (Xbox)'
        else:
            return 'Xbox'
    
    def _extract_genre(self, product: Dict) -> Optional[str]:
        """Extract primary genre from product."""
        try:
            categories = product.get('Properties', {}).get('Categories', [])
            if categories:
                return categories[0].get('Name')
        except:
            pass
        return None
    
    def _is_game_pass(self, product: Dict) -> bool:
        """Check if game is available on Game Pass."""
        try:
            # Check in product properties
            properties = product.get('Properties', {})
            offerings = properties.get('XboxGamePassOffers', [])
            return len(offerings) > 0
        except:
            return False
    
    def _is_dlc(self, title: str, product: Dict = None) -> bool:
        """Check if the product is DLC or add-on."""
        # Check title keywords
        dlc_keywords = [
            'dlc', 'add-on', 'addon', 'expansion', 'season pass',
            'bundle', 'pack', 'edition upgrade', 'content'
        ]
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in dlc_keywords):
            return True
        
        # Check product type
        try:
            product_type = product.get('ProductType', '').lower()
            if 'addon' in product_type or 'dlc' in product_type:
                return True
        except:
            pass
        
        return False
    
    def get_game_details(self, game_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific game.
        
        Args:
            game_id: Xbox product ID
            
        Returns:
            Dictionary with game details
        """
        try:
            # Extract product ID
            product_id = game_id.replace('xbox_', '')
            
            params = {
                'market': self.market,
                'languages': self.language,
                'MS-CV': 'DGU1mcuYo0WMMp+F.1',
                'fieldsTemplate': 'Details'
            }
            
            url = f"{self.BASE_URL}/{product_id}"
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data.get('Products', [{}])[0]
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to fetch details for {game_id}: {e}")
            return None
    
    def fetch_game_pass_games(self) -> List[ConsoleDeal]:
        """
        Fetch games currently on Game Pass using the Recommendation API.
        """
        if not self.include_game_pass:
            return []
        
        try:
            # Using the specific GamePass channel
            gp_url = "https://reco-public.rec.mp.microsoft.com/channels/XboxMarketplace/GamePass"
            params = {
                'market': self.market,
                'languages': self.language,
                'count': 50
            }
            
            self.logger.debug(f"🔍 Fetching Game Pass games from Reco API...")
            response = requests.get(gp_url, params=params, timeout=20)
            response.raise_for_status()
            
            items = response.json().get('Items', [])
            product_ids = [item.get('Id') for item in items if item.get('Id')]
            
            if not product_ids:
                return []
                
            self.logger.info(f"🎮 Found {len(product_ids)} Game Pass IDs")
            return self._fetch_product_details(product_ids)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch Game Pass games: {e}")
            return []
    
    def _parse_game_pass_entry(self, product: Dict) -> Optional[ConsoleDeal]:
        """Parse a Game Pass product entry."""
        try:
            localized_props = product.get('LocalizedProperties', [{}])[0]
            title = localized_props.get('ProductTitle', 'Unknown Game')
            
            # Get pricing (often free with Game Pass)
            properties = product.get('DisplaySkuAvailabilities', [{}])[0]
            availabilities = properties.get('Availabilities', [{}])[0]
            price_info = availabilities.get('OrderManagementData', {}).get('Price', {})
            
            original_price = float(price_info.get('MSRP', 0))
            
            return ConsoleDeal(
                title=title,
                store_url=f"https://www.microsoft.com/en-{self.market}/p/{product.get('ProductId', '')}",
                platform="Xbox",
                console_gen=self._determine_console(product.get('Properties', {}).get('XboxPlatforms', [])),
                
                original_price=original_price,
                current_price=0.0,  # Free with Game Pass
                discount_percent=100,
                currency=price_info.get('CurrencyCode', 'USD'),
                
                game_id=f"gamepass_{product.get('ProductId', '')}",
                release_date=product.get('MarketProperties', [{}])[0].get('OriginalReleaseDate'),
                publisher=localized_props.get('PublisherName', ''),
                developer=localized_props.get('DeveloperName', ''),
                genre=self._extract_genre(product),
                
                is_game_pass=True,
                is_dlc=False
            )
        except:
            return None
    
    def hunt(self, rawg_api_key: Optional[str] = None) -> List[ConsoleDeal]:
        """
        Enhanced hunt including Game Pass games.
        
        Args:
            rawg_api_key: Optional RAWG API key
            
        Returns:
            List of all quality deals (sales + Game Pass)
        """
        self.logger.info("🔍 Starting Xbox hunt...")
        
        # Fetch regular sales
        all_deals = super().hunt(rawg_api_key)
        
        # Fetch Game Pass games if enabled
        if self.include_game_pass:
            game_pass_games = self.fetch_game_pass_games()
            
            # Filter Game Pass games
            filtered_gp = self.filter_deals(game_pass_games)
            
            # Enrich Game Pass games
            for game in filtered_gp:
                enriched = self.enrich_deal(game, rawg_api_key)
                all_deals.append(enriched)
        
        self.logger.info(f"✅ Xbox hunt complete: {len(all_deals)} total deals")
        return all_deals


# Test function
def test_xbox_hunter():
    """Test Xbox hunter with sample config."""
    
    config = {
        'apis': {
            'xbox': {
                'region': 'us',
                'language': 'en-US'
            }
        },
        'filters': {
            'xbox': {
                'min_discount': 50,
                'min_score': 3.5,
                'exclude_dlc': True,
                'include_game_pass': True,
                'max_price': 60
            }
        }
    }
    
    class MockCache:
        def __init__(self):
            self.posted = set()
        def is_posted(self, game_id):
            return game_id in self.posted
        def add_to_cache(self, game_id, data):
            self.posted.add(game_id)
    
    cache = MockCache()
    hunter = XboxHunter(config, cache)
    
    deals = hunter.hunt()
    
    print(f"\n🟩 Xbox Hunter Test Results")
    print(f"{'='*50}")
    print(f"Total deals found: {len(deals)}")
    print(f"\n📋 Sample Deals:")
    
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal.title}")
        print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
        print(f"   📊 {deal.discount_percent}% off")
        print(f"   ⭐ Quality Score: {deal.quality_score:.1f}/5.0")
        print(f"   🎮 Platform: {deal.console_gen}")
        if deal.is_game_pass:
            print(f"   🎮 Game Pass Available")


if __name__ == "__main__":
    test_xbox_hunter()
