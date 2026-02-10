"""
🟩 Xbox Simple Hunter - Using CheapShark
─────────────────────────────────────────

Hunter simple que usa CheapShark API para obtener deals de Xbox.
CheapShark tiene datos confiables de Microsoft Store.

Author: HunDeaBot Team
Version: 1.0.0 - WORKING
"""

import requests
import logging
from typing import List, Dict


def fetch_xbox_deals_cheapshark(max_deals=50, logger=None) -> List[Dict]:
    """
    Fetch Xbox deals from CheapShark (Xbox/Microsoft Store).
    
    Args:
        max_deals: Maximum deals to return
        logger: Optional logger
        
    Returns:
        List of deal dicts
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    deals = []
    
    try:
        logger.info("🦈 Fetching Xbox deals from CheapShark...")
        
        # CheapShark API
        # storeID 15 = Microsoft Store (Xbox/Windows)
        url = "https://www.cheapshark.com/api/1.0/deals"
        
        params = {
            'storeID': '15',  # Microsoft Store
            'onSale': '1',     # Only deals
            'pageSize': max_deals
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"📥 CheapShark returned {len(data)} Xbox deals")
        
        for item in data:
            try:
                # Extract info
                title = item.get('title', 'Unknown')
                normal_price = float(item.get('normalPrice', 0))
                sale_price = float(item.get('salePrice', 0))
                
                # Skip if no discount
                if normal_price == 0 or sale_price >= normal_price:
                    continue
                
                savings = float(item.get('savings', 0))
                deal_id = item.get('dealID', '')
                
                deal = {
                    'name': title,
                    'current_price': sale_price,
                    'original_price': normal_price,
                    'discount_percent': int(savings),
                    'currency': 'USD',
                    'url': f"https://www.cheapshark.com/redirect?dealID={deal_id}",
                    'platform': 'Xbox',
                    'store': 'Microsoft Store',
                    'deal_id': deal_id
                }
                
                deals.append(deal)
                
            except Exception as e:
                logger.debug(f"Error parsing deal: {e}")
                continue
        
        logger.info(f"✅ Processed {len(deals)} Xbox deals")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ CheapShark request failed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    
    return deals


def test_xbox_cheapshark():
    """Test Xbox CheapShark fetcher."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger()
    
    print("\n🧪 Testing Xbox CheapShark Fetcher")
    print("="*60)
    
    deals = fetch_xbox_deals_cheapshark(max_deals=20, logger=logger)
    
    if deals:
        print(f"\n✅ Found {len(deals)} deals\n")
        print("📋 Sample Deals:")
        print("-"*60)
        
        for i, deal in enumerate(deals[:10], 1):
            print(f"\n{i}. {deal['name']}")
            print(f"   💰 ${deal['current_price']:.2f} (was ${deal['original_price']:.2f})")
            print(f"   📊 {deal['discount_percent']}% OFF")
            print(f"   🔗 {deal['url'][:60]}...")
    else:
        print("\n⚠️  No deals found")
        print("💡 Check internet connection or try again later")


if __name__ == "__main__":
    test_xbox_cheapshark()
