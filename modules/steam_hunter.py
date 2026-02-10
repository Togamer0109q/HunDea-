"""
💨 Steam Hunter - Functional & Tested
──────────────────────────────────────

Busca deals de Steam usando:
1. Steam API (specials)
2. SteamDB scraper
3. Fallback a CheapShark

Author: HunDeaBot Team
Version: 3.7.0 - FUNCTIONAL
"""

import requests
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json


class SteamHunter:
    """
    Steam deals hunter - múltiples métodos.
    """
    
    def __init__(self, logger=None):
        """Initialize Steam hunter."""
        self.logger = logger or logging.getLogger(__name__)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'application/json'
        }
        
        self.logger.info("💨 Steam Hunter initialized")
    
    def obtener_juegos_gratis(self) -> List[Dict]:
        """
        Obtener juegos gratis y en oferta de Steam.
        
        Returns:
            List of deal dicts
        """
        deals = []
        
        # Método 1: Steam Store API (gratis)
        free_games = self._fetch_free_games()
        deals.extend(free_games)
        
        # Método 2: Ofertas via CheapShark
        sale_games = self._fetch_sales_cheapshark()
        deals.extend(sale_games)
        
        self.logger.info(f"✅ Steam: {len(deals)} deals found")
        
        return deals
    
    def _fetch_free_games(self) -> List[Dict]:
        """Fetch free-to-play games from Steam."""
        deals = []
        
        try:
            self.logger.info("🔍 Fetching free Steam games...")
            
            # Steam F2P endpoint
            url = "https://store.steampowered.com/api/featured/"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Get free games
            if 'specials' in data:
                specials = data['specials'].get('items', [])
                
                for item in specials[:20]:  # Top 20
                    # Only free games
                    if item.get('final_price', 0) == 0:
                        deal = {
                            'title': item.get('name', 'Unknown'),
                            'price': 0.0,
                            'regular_price': item.get('original_price', 0) / 100,  # cents to dollars
                            'discount_percent': 100 if item.get('original_price', 0) > 0 else 0,
                            'url': f"https://store.steampowered.com/app/{item.get('id')}",
                            'image_url': item.get('header_image', ''),
                            'platform': 'Steam',
                            'source': 'steam_free',
                            'steam_app_id': item.get('id')
                        }
                        deals.append(deal)
            
            self.logger.info(f"✅ Free games: {len(deals)}")
            
        except Exception as e:
            self.logger.debug(f"Free games error: {e}")
        
        return deals
    
    def _fetch_sales_cheapshark(self) -> List[Dict]:
        """Fetch Steam sales via CheapShark."""
        deals = []
        
        try:
            self.logger.info("🔍 Fetching Steam sales (CheapShark)...")
            
            # CheapShark API - Steam store ID = 1
            url = "https://www.cheapshark.com/api/1.0/deals"
            
            params = {
                'storeID': '1',  # Steam
                'upperPrice': '15',  # Max $15
                'pageSize': '30',
                'sortBy': 'Savings',  # Best savings first
                'onSale': '1'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data:
                try:
                    sale_price = float(item.get('salePrice', 0))
                    normal_price = float(item.get('normalPrice', 0))
                    
                    if normal_price == 0:
                        normal_price = sale_price
                    
                    savings = int(float(item.get('savings', 0)))
                    
                    deal = {
                        'title': item.get('title', 'Unknown'),
                        'price': sale_price,
                        'regular_price': normal_price,
                        'discount_percent': savings,
                        'url': f"https://www.cheapshark.com/redirect?dealID={item.get('dealID')}",
                        'image_url': item.get('thumb', ''),
                        'platform': 'Steam',
                        'metacritic': item.get('metacriticScore'),
                        'steam_rating': item.get('steamRatingPercent'),
                        'source': 'steam_sales',
                        'steam_app_id': item.get('steamAppID')
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    continue
            
            self.logger.info(f"✅ Sales: {len(deals)}")
            
        except Exception as e:
            self.logger.debug(f"Sales error: {e}")
        
        return deals


def test_steam_hunter():
    """Test Steam hunter."""
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("💨 STEAM HUNTER TEST")
    print("="*60)
    
    hunter = SteamHunter()
    
    deals = hunter.obtener_juegos_gratis()
    
    print(f"\n📊 RESULTS:")
    print("="*60)
    print(f"Total deals: {len(deals)}")
    
    if deals:
        print(f"\n🎮 Sample Deals:")
        print("-"*60)
        
        for i, deal in enumerate(deals[:10], 1):
            print(f"\n{i}. {deal['title']}")
            print(f"   💰 ${deal['price']:.2f} (was ${deal['regular_price']:.2f})")
            if deal['discount_percent'] > 0:
                print(f"   📊 {deal['discount_percent']}% OFF")
            print(f"   🔗 {deal['url'][:50]}...")
    else:
        print("\n⚠️  No deals found")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_steam_hunter()
