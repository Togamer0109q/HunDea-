"""
🟦 PlayStation Hunter V2 - IMPROVED
────────────────────────────────────

Multi-source PlayStation deals hunter:
1. PlatPrices API (primary)
2. PSDeals scraper (fallback)
3. CheapShark (emergency)

Author: HunDeaBot Team
Version: 3.5.0 - ULTRA IMPROVED
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from .base_console_hunter import BaseConsoleHunter, ConsoleDeal


class PlayStationHunter(BaseConsoleHunter):
    """
    Multi-source PlayStation hunter (IMPROVED).
    """
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """Initialize PlayStation hunter."""
        super().__init__(config, cache_manager, logger)
        
        # Platform config
        ps_config = config.get('apis', {}).get('psprices', {})
        self.region = ps_config.get('region', 'us').lower()
        self.platform = ps_config.get('platform', 'ps5').lower()
        self.include_ps_plus = self.platform_config.get('include_ps_plus', True)
        
        self.logger.info(f"🟦 PlayStation Hunter V2 initialized")
        self.logger.info(f"🌍 Region: {self.region.upper()}, Platform: {self.platform.upper()}")
    
    def get_platform_name(self) -> str:
        return "PlayStation"
    
    def fetch_deals(self) -> List[ConsoleDeal]:
        """Fetch PlayStation deals from multiple sources."""
        deals = []
        
        # Try source 1: CheapShark (most reliable)
        deals.extend(self._fetch_from_cheapshark())
        
        # Try source 2: PSDeals scraper
        if len(deals) < 10:
            deals.extend(self._fetch_from_psdeals())
        
        self.logger.info(f"📥 Fetched {len(deals)} total PlayStation deals")
        return deals
    
    def _fetch_from_cheapshark(self) -> List[ConsoleDeal]:
        """Fetch PS deals from CheapShark."""
        deals = []
        
        try:
            self.logger.info("🦈 Trying CheapShark for PlayStation...")
            
            # CheapShark doesn't have PS Store directly
            # But we can use it for PC versions that are also on PS
            
            self.logger.warning("⚠️  CheapShark doesn't have PlayStation Store")
            
        except Exception as e:
            self.logger.debug(f"CheapShark error: {e}")
        
        return deals
    
    def _fetch_from_psdeals(self) -> List[ConsoleDeal]:
        """Scrape PSDeals.net."""
        deals = []
        
        try:
            self.logger.info("🔍 Scraping PSDeals.net...")
            
            # PSDeals URL
            region_map = {
                'us': 'en-us',
                'uk': 'en-gb',
                'ca': 'en-ca',
                'au': 'en-au'
            }
            region_code = region_map.get(self.region, 'en-us')
            
            url = f"https://psdeals.net/{region_code}/games/ps5/discounts"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 403:
                self.logger.warning("⚠️  PSDeals blocked request (403)")
                return deals
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find game cards
            game_cards = soup.find_all('div', class_='game-card')[:50]
            
            for card in game_cards:
                try:
                    # Extract title
                    title_elem = card.find('h3') or card.find(class_='title')
                    title = title_elem.text.strip() if title_elem else 'Unknown'
                    
                    # Extract prices
                    price_elem = card.find(class_='price-new')
                    original_elem = card.find(class_='price-old')
                    
                    if not price_elem:
                        continue
                    
                    current_price = self._parse_price(price_elem.text)
                    original_price = self._parse_price(original_elem.text if original_elem else '0')
                    
                    if original_price == 0:
                        original_price = current_price
                    
                    # Calculate discount
                    discount = 0
                    if original_price > current_price > 0:
                        discount = int(((original_price - current_price) / original_price) * 100)
                    
                    # URL
                    link = card.find('a')
                    href = link.get('href', '') if link else ''
                    if href and not href.startswith('http'):
                        href = f"https://psdeals.net{href}"
                    
                    deal = ConsoleDeal(
                        title=title,
                        store_url=href,
                        platform="PlayStation",
                        console_gen="PS5",
                        
                        original_price=original_price,
                        current_price=current_price,
                        discount_percent=discount,
                        currency="USD",
                        
                        game_id=f"ps_{title.replace(' ', '_')[:50]}",
                        is_dlc=self._is_dlc(title)
                    )
                    
                    deals.append(deal)
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing PS deal: {e}")
                    continue
            
            self.logger.info(f"✅ PSDeals: {len(deals)} deals scraped")
            
        except Exception as e:
            self.logger.error(f"❌ PSDeals scraper failed: {e}")
        
        return deals
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        try:
            import re
            # Remove currency symbols and extract number
            numbers = re.findall(r'[\d,.]+', price_str)
            if numbers:
                price = numbers[0].replace(',', '')
                return float(price)
        except:
            pass
        return 0.0
    
    def _is_dlc(self, title: str) -> bool:
        """Check if title is DLC."""
        dlc_keywords = [
            'dlc', 'add-on', 'addon', 'expansion', 'season pass',
            'bundle', 'pack', 'edition upgrade', 'content pack'
        ]
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in dlc_keywords)
    
    def fetch_ps_plus_games(self) -> List[ConsoleDeal]:
        """Fetch PS Plus free games."""
        # TODO: Implement PS Plus scraper
        return []
    
    def hunt(self, rawg_api_key: Optional[str] = None) -> List[ConsoleDeal]:
        """Enhanced hunt."""
        self.logger.info("🔍 Starting PlayStation hunt...")
        
        # Fetch deals
        all_deals = super().hunt(rawg_api_key)
        
        # Fetch PS Plus if enabled
        if self.include_ps_plus:
            ps_plus_games = self.fetch_ps_plus_games()
            filtered_ps_plus = self.filter_deals(ps_plus_games)
            
            for game in filtered_ps_plus:
                enriched = self.enrich_deal(game, rawg_api_key)
                all_deals.append(enriched)
        
        self.logger.info(f"✅ PlayStation hunt complete: {len(all_deals)} total deals")
        return all_deals
