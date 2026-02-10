"""
🎁 GamerPower Hunter - FREE Games & Giveaways
──────────────────────────────────────────────

Uses GamerPower API (100% FREE, no key needed!)
https://www.gamerpower.com/api-read

Tracks:
- Free games
- Free weekends  
- Giveaways
- Beta access

Author: HunDeaBot Team
Version: 4.0.0 - GAMERPOWER GOLD
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime


class GamerPowerHunter:
    """
    GamerPower API hunter - FREE games, weekends, giveaways.
    
    API is 100% FREE - no key required!
    """
    
    BASE_URL = "https://www.gamerpower.com/api"
    
    def __init__(self, logger=None):
        """Initialize GamerPower hunter."""
        self.logger = logger or logging.getLogger(__name__)
        
        self.headers = {
            'User-Agent': 'HunDeaBot/4.0.0'
        }
        
        self.logger.info("🎁 GamerPower Hunter initialized")
        self.logger.info("   100% FREE API - No key needed!")
    
    def hunt_all_free(self) -> List[Dict]:
        """
        Get ALL free stuff: games, weekends, giveaways.
        
        Returns:
            List of giveaway dicts
        """
        all_giveaways = []
        
        # Get all active giveaways
        giveaways = self._fetch_all_giveaways()
        all_giveaways.extend(giveaways)
        
        self.logger.info(f"✅ GamerPower: {len(all_giveaways)} giveaways/freebies")
        
        return all_giveaways

    def fetch_deals(self) -> List[Dict]:
        """Adapter for MegaAPIAggregator fetch method."""
        return self.hunt_all_free()
    
    def hunt_pc_only(self) -> List[Dict]:
        """Get PC-only giveaways."""
        return self._fetch_by_platform('pc')
    
    def hunt_steam_only(self) -> List[Dict]:
        """Get Steam-only giveaways."""
        return self._fetch_by_platform('steam')
    
    def hunt_epic_only(self) -> List[Dict]:
        """Get Epic Games-only giveaways."""
        return self._fetch_by_platform('epic-games-store')
    
    def _fetch_all_giveaways(self) -> List[Dict]:
        """Fetch all active giveaways."""
        deals = []
        
        try:
            url = f"{self.BASE_URL}/giveaways"
            
            self.logger.debug(f"Fetching: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    deal = self._parse_giveaway(item)
                    if deal:
                        deals.append(deal)
            
            self.logger.debug(f"Fetched {len(deals)} giveaways")
            
        except Exception as e:
            self.logger.error(f"Error fetching giveaways: {e}")
        
        return deals
    
    def _fetch_by_platform(self, platform: str) -> List[Dict]:
        """Fetch giveaways by platform."""
        deals = []
        
        try:
            url = f"{self.BASE_URL}/giveaways"
            params = {'platform': platform}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    deal = self._parse_giveaway(item)
                    if deal:
                        deals.append(deal)
            
        except Exception as e:
            self.logger.debug(f"Error fetching {platform}: {e}")
        
        return deals
    
    def _parse_giveaway(self, item: Dict) -> Optional[Dict]:
        """Parse giveaway from API response."""
        try:
            # Determine type
            giveaway_type = item.get('type', 'Game').lower()
            
            # Check if it's free weekend
            is_free_weekend = 'free weekend' in item.get('title', '').lower()
            is_free_weekend = is_free_weekend or 'free to play' in giveaway_type
            
            deal = {
                'id': f"gp_{item.get('id')}",
                'title': item.get('title', 'Unknown'),
                'description': item.get('description', ''),
                'url': item.get('open_giveaway_url') or item.get('gamerpower_url'),
                'image': item.get('image'),
                'thumbnail': item.get('thumbnail'),
                
                # Type info
                'type': giveaway_type,
                'is_free_weekend': is_free_weekend,
                'worth': item.get('worth', 'N/A'),
                
                # Platform info
                'platforms': item.get('platforms', '').split(', '),
                
                # Dates
                'end_date': item.get('end_date'),
                'published_date': item.get('published_date'),
                
                # Instructions
                'instructions': item.get('instructions'),
                
                # Source
                'source': 'GamerPower'
            }
            
            return deal
            
        except Exception as e:
            self.logger.debug(f"Parse error: {e}")
            return None
    
    def filter_free_weekends(self, giveaways: List[Dict]) -> List[Dict]:
        """Filter only FREE WEEKENDS."""
        free_weekends = []
        
        for g in giveaways:
            if g.get('is_free_weekend'):
                free_weekends.append(g)
        
        return free_weekends


def test_gamerpower():
    """Test GamerPower hunter."""
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🎁 GAMERPOWER HUNTER TEST")
    print("="*70)
    print()
    
    hunter = GamerPowerHunter()
    
    # Fetch all
    print("🔍 Fetching ALL giveaways...")
    all_giveaways = hunter.hunt_all_free()
    
    # Filter free weekends
    free_weekends = hunter.filter_free_weekends(all_giveaways)
    
    print(f"\n📊 RESULTS:")
    print("="*70)
    print(f"Total giveaways: {len(all_giveaways)}")
    print(f"Free weekends: {len(free_weekends)}")
    
    if all_giveaways:
        print(f"\n🎁 Sample Giveaways (first 5):")
        print("-"*70)
        
        for i, g in enumerate(all_giveaways[:5], 1):
            weekend = "🆓 FREE WEEKEND" if g['is_free_weekend'] else ""
            print(f"\n{i}. {g['title']} {weekend}")
            print(f"   Type: {g['type']}")
            print(f"   Worth: {g['worth']}")
            print(f"   Platforms: {', '.join(g['platforms'])}")
            print(f"   URL: {g['url'][:60]}...")
    
    if free_weekends:
        print(f"\n\n🆓 FREE WEEKENDS FOUND:")
        print("-"*70)
        
        for i, fw in enumerate(free_weekends, 1):
            print(f"\n{i}. {fw['title']}")
            print(f"   Platforms: {', '.join(fw['platforms'])}")
            print(f"   End: {fw['end_date']}")
    
    print("\n" + "="*70)
    print()


if __name__ == "__main__":
    test_gamerpower()
