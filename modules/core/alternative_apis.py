"""
🌐 Alternative API Implementations - Web Scraping Fallback
──────────────────────────────────────────────────────────

When official APIs fail, these scrapers provide fallback data.
Uses BeautifulSoup for simple HTML parsing.

Author: HunDeaBot Team
Version: 3.0.0
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import re


logger = logging.getLogger(__name__)


class PSStoreScraperUS:
    """Scrape PlayStation Store deals from PSDeals.net"""
    
    BASE_URL = "https://psdeals.net"
    
    @staticmethod
    def fetch_deals(platform='ps5', region='us') -> List[Dict]:
        """
        Fetch PS deals from PSDeals.net
        
        Args:
            platform: ps4, ps5
            region: us, uk, eu
            
        Returns:
            List of deal dictionaries
        """
        deals = []
        
        try:
            # PSDeals.net URL structure
            url = f"{PSStoreScraperUS.BASE_URL}/en-{region}/games/{platform}/discounts"
            logger.debug(f"🔍 Scraping: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find game cards (structure may vary)
            game_cards = soup.find_all('div', class_='game-collection-item')
            
            for card in game_cards[:50]:  # Limit to 50 deals
                try:
                    # Extract game title
                    title_elem = card.find('span', class_='game-collection-item-name')
                    title = title_elem.text.strip() if title_elem else 'Unknown'
                    
                    # Extract prices
                    price_new = card.find('span', class_='game-collection-item-price-new')
                    price_old = card.find('span', class_='game-collection-item-price-old')
                    
                    if not price_new or not price_old:
                        continue
                    
                    current_price = PSStoreScraperUS._parse_price(price_new.text)
                    original_price = PSStoreScraperUS._parse_price(price_old.text)
                    
                    if current_price == 0 or original_price == 0:
                        continue
                    
                    # Calculate discount
                    discount = int(((original_price - current_price) / original_price) * 100)
                    
                    # Extract link
                    link_elem = card.find('a', class_='game-collection-item-link')
                    game_url = PSStoreScraperUS.BASE_URL + link_elem['href'] if link_elem else ''
                    
                    # Build deal dict
                    deal = {
                        'id': PSStoreScraperUS._extract_id_from_url(game_url),
                        'name': title,
                        'url': game_url,
                        'price': {
                            'base_price': int(original_price * 100),
                            'discounted_price': int(current_price * 100)
                        },
                        'platforms': [platform.upper()],
                        'discount_percent': discount
                    }
                    
                    deals.append(deal)
                    
                except Exception as e:
                    logger.debug(f"Failed to parse game card: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(deals)} PS deals from PSDeals.net")
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
        
        return deals
    
    @staticmethod
    def _parse_price(price_text: str) -> float:
        """Extract numeric price from text like '$29.99' or '€19.99'"""
        try:
            # Remove currency symbols and extract number
            clean = re.sub(r'[^\d.]', '', price_text)
            return float(clean) if clean else 0.0
        except:
            return 0.0
    
    @staticmethod
    def _extract_id_from_url(url: str) -> str:
        """Extract game ID from URL"""
        try:
            # URLs like: /en-us/game/12345/game-name
            match = re.search(r'/game/(\d+)/', url)
            return match.group(1) if match else url
        except:
            return url


class XboxStoreScraperUS:
    """Scrape Xbox deals from TrueAchievements or XboxStore"""
    
    @staticmethod
    def fetch_deals(market='us') -> List[Dict]:
        """
        Fetch Xbox deals - simplified version
        Returns mock data until real scraper is implemented
        """
        logger.warning("⚠️  Xbox scraper not fully implemented - using CheapShark as fallback")
        
        # Fallback: Use CheapShark for Xbox PC games
        try:
            url = "https://www.cheapshark.com/api/1.0/deals"
            params = {
                'storeID': '2',  # Microsoft Store
                'onSale': '1',
                'pageSize': 50
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            deals_data = response.json()
            deals = []
            
            for item in deals_data:
                deal = {
                    'ProductId': item.get('dealID', ''),
                    'LocalizedProperties': [{
                        'ProductTitle': item.get('title', 'Unknown Game')
                    }],
                    'DisplaySkuAvailabilities': [{
                        'Availabilities': [{
                            'OrderManagementData': {
                                'Price': {
                                    'MSRP': float(item.get('normalPrice', 0)),
                                    'ListPrice': float(item.get('salePrice', 0)),
                                    'CurrencyCode': 'USD'
                                }
                            }
                        }]
                    }],
                    'Properties': {
                        'XboxPlatforms': ['PC']
                    }
                }
                deals.append(deal)
            
            logger.info(f"✅ Fetched {len(deals)} Xbox PC deals via CheapShark")
            return deals
            
        except Exception as e:
            logger.error(f"❌ Xbox fallback failed: {e}")
            return []


class NintendoStoreScraper:
    """Scrape Nintendo eShop deals"""
    
    @staticmethod
    def fetch_deals(region='us') -> List[Dict]:
        """
        Fetch Nintendo deals - simplified version
        Returns sample structure for testing
        """
        logger.warning("⚠️  Nintendo scraper not fully implemented")
        
        # Could implement scraping from:
        # - eshop-prices.com
        # - dekudeals.com (requires more complex scraping)
        # - Nintendo's own API (if available)
        
        return []


def test_scrapers():
    """Test all scrapers"""
    
    print("\n🧪 Testing Alternative Scrapers")
    print("="*60)
    
    # Test PlayStation
    print("\n🟦 Testing PlayStation Scraper...")
    ps_deals = PSStoreScraperUS.fetch_deals(platform='ps5', region='us')
    print(f"✅ Found {len(ps_deals)} PS deals")
    if ps_deals:
        sample = ps_deals[0]
        print(f"📋 Sample: {sample['name']} - ${sample['price']['discounted_price']/100:.2f}")
    
    # Test Xbox
    print("\n🟩 Testing Xbox Scraper...")
    xbox_deals = XboxStoreScraperUS.fetch_deals()
    print(f"✅ Found {len(xbox_deals)} Xbox deals")
    
    # Test Nintendo
    print("\n🟥 Testing Nintendo Scraper...")
    nintendo_deals = NintendoStoreScraper.fetch_deals()
    print(f"✅ Found {len(nintendo_deals)} Nintendo deals")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_scrapers()
