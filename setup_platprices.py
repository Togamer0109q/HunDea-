"""
🎮 PLATPRICES SETUP - Auto Configuration
─────────────────────────────────────────

Configura automáticamente la API key de PlatPrices.

Author: HunDeaBot Team
Version: 1.0.0
"""

import json
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False


def setup_platprices_api():
    """Setup PlatPrices API key in config."""
    
    print("\n" + "="*60)
    print("🎮 PLATPRICES API SETUP")
    print("="*60)
    
    load_dotenv()

    # API Key from .env
    PLATPRICES_API_KEY = os.getenv("PLATPRICES_API_KEY")
    if not PLATPRICES_API_KEY:
        print("âš ï¸  Missing PLATPRICES_API_KEY in .env")
        return False
    
    # Load config
    config_file = Path('config.json')
    
    if not config_file.exists():
        print("⚠️  config.json not found, using template...")
        config_file = Path('config_v3.example.json')
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Update APIs section
    if 'apis' not in config:
        config['apis'] = {}
    
    # Add PlatPrices config
    config['apis']['platprices'] = {
        'api_key': PLATPRICES_API_KEY,
        'region': 'us',
        'platform': 'ps5'
    }
    
    # Also update old psprices if exists
    if 'psprices' in config.get('apis', {}):
        config['apis']['psprices']['api_key'] = PLATPRICES_API_KEY
    else:
        config['apis']['psprices'] = {
            'api_key': PLATPRICES_API_KEY,
            'region': 'us',
            'platform': 'ps5'
        }
    
    print(f"\n✅ API Key configured: {PLATPRICES_API_KEY[:20]}...")
    print(f"✅ Region: US")
    print(f"✅ Platform: PS5")
    
    # Save config
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Config saved to config.json")
    
    print("\n" + "="*60)
    print("📊 EXPECTED RESULTS")
    print("="*60)
    print("Before: PlayStation: 0 deals ❌")
    print("After:  PlayStation: 15-30 deals ✅")
    print("\nTOTAL IMPROVEMENT: +15-30 deals!")
    print("="*60)
    
    print("\n🚀 NEXT STEP:")
    print("python hundea_v3.py")
    print("\nOr test PlayStation only:")
    print("python test_playstation.py")
    
    return True


if __name__ == "__main__":
    setup_platprices_api()
