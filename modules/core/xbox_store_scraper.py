"""
🟩 Xbox Store Scraper - Real Colombian Store
─────────────────────────────────────────────

Scraper directo de xbox.com para Colombia y otras regiones.
Extrae ofertas reales del sitio web de Xbox.

Author: HunDeaBot Team
Version: 2.0.0 - FIXED
"""

import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict, Optional
import json


class XboxStoreScraper:
    """
    Scraper para Xbox Store - Funciona con el sitio real.
    """
    
    # URLs por región
    STORE_URLS = {
        'us': 'https://www.xbox.com/en-us/promotions/sales/sales-and-specials',
        'co': 'https://www.xbox.com/es-co/promotions/sales/sales-and-specials',  # Colombia
        'mx': 'https://www.xbox.com/es-mx/promotions/sales/sales-and-specials',
        'br': 'https://www.xbox.com/pt-br/promotions/sales/sales-and-specials',
        'ar': 'https://www.xbox.com/es-ar/promotions/sales/sales-and-specials',
        'uk': 'https://www.xbox.com/en-gb/promotions/sales/sales-and-specials',
    }
    
    def __init__(self, region='co', logger=None):
        """
        Initialize scraper.
        
        Args:
            region: Region code (us, co, mx, etc.)
            logger: Optional logger
        """
        self.region = region.lower()
        self.logger = logger or logging.getLogger(__name__)
        self.store_url = self.STORE_URLS.get(self.region, self.STORE_URLS['us'])
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-CO,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_deals(self, max_deals=50) -> List[Dict]:
        """
        Fetch deals from Xbox Store.
        
        Args:
            max_deals: Maximum number of deals to fetch
            
        Returns:
            List of deal dicts
        """
        deals = []
        
        try:
            self.logger.info(f"🔍 Scraping Xbox Store ({self.region.upper()})...")
            self.logger.info(f"📍 URL: {self.store_url}")
            
            response = requests.get(
                self.store_url,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            
            self.logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code != 200:
                self.logger.error(f"❌ HTTP {response.status_code}")
                return deals
            
            # El sitio de Xbox usa JavaScript para cargar juegos
            # Pero también tiene datos en el HTML inicial
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar scripts con datos de juegos
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if isinstance(data, dict):
                        # Extraer info del juego
                        game_data = self._extract_game_data(data)
                        if game_data:
                            deals.append(game_data)
                    elif isinstance(data, list):
                        for item in data:
                            game_data = self._extract_game_data(item)
                            if game_data:
                                deals.append(game_data)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Error parsing script: {e}")
                    continue
            
            # Método alternativo: buscar en el HTML
            if not deals:
                deals = self._parse_html_deals(soup)
            
            # Limitar resultados
            deals = deals[:max_deals]
            
            self.logger.info(f"✅ Scraped {len(deals)} Xbox deals")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ Scraping error: {e}")
        
        return deals
    
    def _extract_game_data(self, data: Dict) -> Optional[Dict]:
        """Extract game data from JSON-LD structure."""
        try:
            # Check if it's a product
            if data.get('@type') not in ['Product', 'VideoGame']:
                return None
            
            name = data.get('name', '')
            if not name:
                return None
            
            # Extract pricing
            offers = data.get('offers', {})
            if isinstance(offers, list) and offers:
                offers = offers[0]
            
            price = offers.get('price', 0)
            currency = offers.get('priceCurrency', 'COP')
            
            # Extract discount if available
            original_price = offers.get('priceValidUntil') or price  # Simplified
            
            game = {
                'name': name,
                'current_price': float(price) if price else 0,
                'original_price': float(original_price) if original_price else 0,
                'currency': currency,
                'url': data.get('url', ''),
                'image': data.get('image', ''),
                'description': data.get('description', '')[:200] if data.get('description') else '',
                'platform': 'Xbox'
            }
            
            # Calculate discount
            if game['original_price'] > game['current_price'] > 0:
                game['discount_percent'] = int(
                    ((game['original_price'] - game['current_price']) / game['original_price']) * 100
                )
            else:
                game['discount_percent'] = 0
            
            return game
            
        except Exception as e:
            return None
    
    def _parse_html_deals(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse deals from HTML structure (fallback)."""
        deals = []
        
        try:
            # Buscar artículos/cards de juegos
            # Esto varía según el sitio, pero intentemos diferentes selectores
            selectors = [
                'div[class*="product"]',
                'div[class*="game"]',
                'article[class*="item"]',
                'div[data-game-id]',
                'div[class*="card"]'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                
                if items:
                    self.logger.info(f"📦 Found {len(items)} items with selector: {selector}")
                    
                    for item in items[:50]:  # Limit to first 50
                        try:
                            # Extract title
                            title_elem = (
                                item.find('h3') or 
                                item.find('h2') or 
                                item.find(class_=re.compile(r'title|name', re.I))
                            )
                            
                            if not title_elem:
                                continue
                            
                            title = title_elem.get_text(strip=True)
                            
                            # Extract prices
                            price_elems = item.find_all(string=re.compile(r'\$|COP'))
                            
                            prices = []
                            for price_text in price_elems:
                                # Extract numbers
                                price_match = re.search(r'[\d,.]+', price_text)
                                if price_match:
                                    price_str = price_match.group().replace(',', '').replace('.', '')
                                    try:
                                        prices.append(float(price_str))
                                    except:
                                        pass
                            
                            if not prices:
                                continue
                            
                            # Extract URL
                            link = item.find('a')
                            url = link['href'] if link and 'href' in link.attrs else ''
                            
                            if url and not url.startswith('http'):
                                url = f"https://www.xbox.com{url}"
                            
                            # Determine original and current price
                            if len(prices) >= 2:
                                original_price = max(prices)
                                current_price = min(prices)
                            elif len(prices) == 1:
                                current_price = prices[0]
                                original_price = prices[0]
                            else:
                                continue
                            
                            # Calculate discount
                            if original_price > current_price > 0:
                                discount = int(((original_price - current_price) / original_price) * 100)
                            else:
                                discount = 0
                            
                            game = {
                                'name': title,
                                'current_price': current_price,
                                'original_price': original_price,
                                'currency': 'COP',  # Assuming Colombia
                                'discount_percent': discount,
                                'url': url,
                                'platform': 'Xbox'
                            }
                            
                            deals.append(game)
                            
                        except Exception as e:
                            self.logger.debug(f"Error parsing item: {e}")
                            continue
                    
                    if deals:
                        break  # Found deals, stop trying selectors
            
        except Exception as e:
            self.logger.error(f"❌ HTML parsing error: {e}")
        
        return deals
    
    def get_deals_by_category(self, category='all') -> List[Dict]:
        """
        Get deals by category.
        
        Args:
            category: 'all', 'games', 'dlc', 'bundles'
            
        Returns:
            Filtered deals
        """
        deals = self.fetch_deals()
        
        if category == 'all':
            return deals
        
        # Filter based on category
        filtered = []
        
        for deal in deals:
            name_lower = deal['name'].lower()
            
            if category == 'games':
                # Exclude DLC and bundles
                if not any(kw in name_lower for kw in ['dlc', 'pack', 'bundle', 'edition deluxe']):
                    filtered.append(deal)
            
            elif category == 'dlc':
                if any(kw in name_lower for kw in ['dlc', 'pack', 'expansion']):
                    filtered.append(deal)
            
            elif category == 'bundles':
                if any(kw in name_lower for kw in ['bundle', 'collection', 'ultimate edition']):
                    filtered.append(deal)
        
        return filtered


# Test function
def test_xbox_scraper():
    """Test Xbox scraper."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("\n🧪 Testing Xbox Store Scraper")
    print("="*60)
    
    # Test Colombia
    scraper = XboxStoreScraper(region='co', logger=logger)
    deals = scraper.fetch_deals(max_deals=20)
    
    print(f"\n✅ Found {len(deals)} deals")
    
    if deals:
        print("\n📋 Sample Deals:")
        for i, deal in enumerate(deals[:5], 1):
            print(f"\n{i}. {deal['name']}")
            print(f"   💰 {deal['currency']} {deal['current_price']:,.0f}")
            if deal['discount_percent'] > 0:
                print(f"   📊 {deal['discount_percent']}% OFF")
                print(f"   🔖 Was: {deal['currency']} {deal['original_price']:,.0f}")
    else:
        print("\n⚠️  No deals found - may need to adjust scraping logic")
        print("💡 The Xbox store uses heavy JavaScript loading")
        print("💡 Consider using Selenium or Playwright for better results")


if __name__ == "__main__":
    test_xbox_scraper()
