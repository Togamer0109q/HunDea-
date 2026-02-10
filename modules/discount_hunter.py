"""
💰 DISCOUNT HUNTER - The Ultimate Deal Finder
─────────────────────────────────────────────

Combines multiple "Iron" APIs to find "Gold":
1. CheapShark API (General Discounts)
2. GamerPower API (Giveaways)
3. IsThereAnyDeal (Optional/Advanced)

Author: HunDeaBot Team
Version: 1.0.0
"""

import logging
from typing import List, Dict, Optional
from modules.cheapshark_hunter import CheapSharkHunter
from modules.gamerpower_hunter import GamerPowerHunter

class DiscountHunter:
    """
    Master Discount Hunter.
    Orchestrates multiple hunters to find the best deals.
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.cheapshark = CheapSharkHunter(logger=self.logger)
        self.gamerpower = GamerPowerHunter(logger=self.logger)
        
    def hunt_all_discounts(self, min_discount: int = 70) -> Dict[str, List[Dict]]:
        """
        Hunt for ALL discounts and freebies.
        
        Args:
            min_discount: Minimum discount percentage (default 70%)
            
        Returns:
            Dict with 'free' and 'discounts' lists
        """
        self.logger.info("")
        self.logger.info("="*60)
        self.logger.info(f"💰 STARTING DISCOUNT HUNT (Min: {min_discount}%)")
        self.logger.info("="*60)
        
        # 1. Get Giveaways (Gold Source 1)
        giveaways = self.gamerpower.hunt_all_free()
        
        # 2. Get Deep Discounts (Gold Source 2)
        discounts = self.cheapshark.obtener_ofertas_descuento(descuento_minimo=min_discount)
        
        # 3. Get Free Games from CheapShark (Double Check)
        cs_free = self.cheapshark.obtener_juegos_gratis()
        
        # Merge free lists (simple de-duplication based on title)
        all_free = giveaways + cs_free
        unique_free = self._deduplicate_deals(all_free)
        
        results = {
            'free_games': unique_free,
            'discounts': discounts
        }
        
        self.logger.info("")
        self.logger.info("="*60)
        self.logger.info("📊 DISCOUNT HUNT SUMMARY")
        self.logger.info("="*60)
        self.logger.info(f"🎁 Free Games: {len(unique_free)}")
        self.logger.info(f"💰 Deep Discounts: {len(discounts)}")
        self.logger.info("="*60)
        
        return results
    
    def _deduplicate_deals(self, deals: List[Dict]) -> List[Dict]:
        """Remove duplicates based on title."""
        seen = set()
        unique = []
        
        for deal in deals:
            # Normalize title
            title = deal.get('titulo') or deal.get('title')
            if not title:
                continue
                
            norm_title = title.lower().strip()
            
            if norm_title not in seen:
                seen.add(norm_title)
                unique.append(deal)
        
        return unique

def test_discount_hunter():
    """Test the Discount Hunter."""
    logging.basicConfig(level=logging.INFO)
    
    hunter = DiscountHunter()
    results = hunter.hunt_all_discounts(min_discount=80)
    
    print("")
    print("📦 SAMPLE RESULTS:")
    
    if results['free_games']:
        print("")
        print(f"🎁 Top 3 Free Games:")
        for g in results['free_games'][:3]:
            title = g.get('titulo') or g.get('title')
            print(f"   - {title}")
            
    if results['discounts']:
        print("")
        print(f"💰 Top 3 Deep Discounts (80%+):")
        for d in results['discounts'][:3]:
            print(f"   - {d['titulo']} (-{d['descuento_porcentaje']}%)")

if __name__ == "__main__":
    test_discount_hunter()
