"""
🟪 GOG Hunter - DRM-Free Deals
───────────────────────────────

Busca deals de GOG.com (Good Old Games):
- Juegos DRM-free
- Ofertas y sales
- Juegos gratis

Author: HunDeaBot Team
Version: 3.7.0 - FUNCTIONAL
"""

import requests
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json


class GOGHunter:
    """
    GOG.com deals hunter.
    """
    
    GOG_API = "https://www.gog.com/games/ajax/filtered"
    
    def __init__(self, logger=None):
        """Initialize GOG hunter."""
        self.logger = logger or logging.getLogger(__name__)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'application/json'
        }
        
        self.logger.info("🟪 GOG Hunter initialized")
    
    def obtener_juegos_gratis(self) -> List[Dict]:
        """
        Obtener juegos gratis y en oferta de GOG.
        
        Returns:
            List of deal dicts
        """
        deals = []
        
        # Método 1: Ofertas de GOG
        sales = self._fetch_sales()
        deals.extend(sales)
        
        # Método 2: Juegos gratis
        free = self._fetch_free_games()
        deals.extend(free)
        
        self.logger.info(f"✅ GOG: {len(deals)} deals found")
        
        return deals
    
    def _fetch_sales(self) -> List[Dict]:
        """Fetch GOG sales."""
        deals = []
        
        try:
            self.logger.info("🔍 Fetching GOG sales...")
            
            # GOG filtered API
            params = {
                'mediaType': 'game',
                'page': '1',
                'sort': 'popularity',
                'promo': 'true',  # Only promos
                'limit': '48'
            }
            
            response = requests.get(
                self.GOG_API,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            products = data.get('products', [])
            
            for product in products:
                try:
                    # Get prices
                    price_obj = product.get('price', {})
                    
                    base_price = float(price_obj.get('baseAmount', 0) or 0)
                    final_price = float(price_obj.get('finalAmount', 0) or 0)
                    discount_pct = int(price_obj.get('discountPercentage', 0) or 0)
                    
                    # Convert from cents/smallest unit
                    if base_price > 100:  # Probably in cents
                        base_price = base_price / 100
                        final_price = final_price / 100
                    
                    # Skip if no discount
                    if discount_pct == 0:
                        continue
                    
                    # Get URL
                    slug = product.get('slug', '')
                    url = f"https://www.gog.com/game/{slug}" if slug else ''
                    
                    # Get image
                    image = product.get('image', '')
                    if image and not image.startswith('http'):
                        image = f"https:{image}"
                    
                    deal = {
                        'title': product.get('title', 'Unknown'),
                        'price': final_price,
                        'regular_price': base_price,
                        'discount_percent': discount_pct,
                        'url': url,
                        'image_url': image,
                        'platform': 'GOG',
                        'drm_free': True,
                        'source': 'gog_sales'
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    continue
            
            self.logger.info(f"✅ Sales: {len(deals)}")
            
        except Exception as e:
            self.logger.debug(f"GOG sales error: {e}")
        
        return deals
    
    def _fetch_free_games(self) -> List[Dict]:
        """Fetch free GOG games."""
        deals = []
        
        try:
            self.logger.info("🔍 Checking GOG free games...")
            
            # GOG sometimes has free games
            params = {
                'mediaType': 'game',
                'page': '1',
                'price': 'free',  # Free games
                'limit': '20'
            }
            
            response = requests.get(
                self.GOG_API,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    try:
                        price_obj = product.get('price', {})
                        
                        # Only truly free
                        if float(price_obj.get('finalAmount', 1)) == 0:
                            slug = product.get('slug', '')
                            url = f"https://www.gog.com/game/{slug}" if slug else ''
                            
                            image = product.get('image', '')
                            if image and not image.startswith('http'):
                                image = f"https:{image}"
                            
                            deal = {
                                'title': product.get('title', 'Unknown'),
                                'price': 0.0,
                                'regular_price': 0.0,
                                'discount_percent': 100,
                                'url': url,
                                'image_url': image,
                                'platform': 'GOG',
                                'drm_free': True,
                                'source': 'gog_free'
                            }
                            
                            deals.append(deal)
                    
                    except Exception as e:
                        continue
                
                self.logger.info(f"✅ Free games: {len(deals)}")
        
        except Exception as e:
            self.logger.debug(f"Free games error: {e}")
        
        return deals


def test_gog_hunter():
    """Test GOG hunter."""
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🟪 GOG HUNTER TEST")
    print("="*60)
    
    hunter = GOGHunter()
    
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
            print(f"   📊 {deal['discount_percent']}% OFF")
            print(f"   🔓 DRM-Free: {deal['drm_free']}")
    else:
        print("\n⚠️  No deals found")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_gog_hunter()
