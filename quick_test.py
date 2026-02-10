"""
🧪 Quick Test - HunDeaBot
──────────────────────────

Script rápido para testear que todo funciona.
"""

import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("\n1️⃣ Testing imports...")
    
    try:
        from modules.consoles.xbox_hunter import XboxHunter
        print("  ✅ XboxHunter")
    except Exception as e:
        print(f"  ❌ XboxHunter: {e}")
        return False
    
    try:
        from modules.core.xbox_store_scraper import XboxStoreScraper
        print("  ✅ XboxStoreScraper")
    except Exception as e:
        print(f"  ❌ XboxStoreScraper: {e}")
        return False
    
    try:
        from modules.core.cache_manager import CacheManager
        print("  ✅ CacheManager")
    except Exception as e:
        print(f"  ❌ CacheManager: {e}")
        return False
    
    return True


def test_xbox_cheapshark():
    """Test Xbox CheapShark fetcher."""
    print("\n2️⃣ Testing Xbox CheapShark...")
    
    try:
        from modules.core.xbox_cheapshark import fetch_xbox_deals_cheapshark
        
        deals = fetch_xbox_deals_cheapshark(max_deals=10)
        
        print(f"  ✅ Found {len(deals)} deals")
        
        if deals:
            print("\n  📋 Sample deals:")
            for i, deal in enumerate(deals[:3], 1):
                print(f"    {i}. {deal['name']}")
                print(f"       💰 ${deal['current_price']:.2f}")
                if deal['discount_percent'] > 0:
                    print(f"       📊 {deal['discount_percent']}% OFF")
            return True
        else:
            print("  ⚠️  No deals found")
            print("  💡 Check internet connection or try again later")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_xbox_hunter():
    """Test Xbox hunter."""
    print("\n3️⃣ Testing Xbox hunter...")
    
    try:
        from modules.core.xbox_cheapshark import fetch_xbox_deals_cheapshark
        
        deals = fetch_xbox_deals_cheapshark(max_deals=10)
        
        print(f"  ✅ CheapShark returned {len(deals)} deals")
        
        if deals:
            print("\n  📋 Sample deals:")
            for i, deal in enumerate(deals[:3], 1):
                print(f"    {i}. {deal['name']}")
                print(f"       💰 ${deal['current_price']:.2f}")
                print(f"       📊 {deal['discount_percent']}% OFF")
            return True
        else:
            print("  ⚠️  No deals found")
            print("  💡 Check internet connection")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test config loading."""
    print("\n4️⃣ Testing config...")
    
    config_files = [
        'config.json',
        'config_testing.json',
        'config_v3.example.json'
    ]
    
    found = False
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {config_file} exists")
            found = True
            
            # Try loading
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Check filters
                if 'filters' in config:
                    xbox_filters = config['filters'].get('xbox', {})
                    min_discount = xbox_filters.get('min_discount', 0)
                    max_price = xbox_filters.get('max_price', 0)
                    
                    print(f"    📊 Xbox filters:")
                    print(f"       min_discount: {min_discount}%")
                    print(f"       max_price: {max_price}")
                    
                    if min_discount > 50:
                        print(f"    ⚠️  min_discount is very high ({min_discount}%)")
                        print(f"    💡 Consider lowering to 20-30%")
                    
                    if max_price < 100000:
                        print(f"    ⚠️  max_price is low ({max_price})")
                        print(f"    💡 For COP, use 200000-500000")
            
            except Exception as e:
                print(f"  ❌ Error loading {config_file}: {e}")
        else:
            print(f"  ⚠️  {config_file} not found")
    
    return found


def main():
    """Run all tests."""
    print("="*60)
    print("🧪 HunDeaBot Quick Test")
    print("="*60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.WARNING,  # Solo warnings y errores
        format='%(levelname)s - %(message)s'
    )
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Xbox CheapShark", test_xbox_cheapshark()))
    results.append(("Xbox Simple Test", test_xbox_hunter()))
    results.append(("Config", test_config()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Bot should work.")
        print("\n💡 Next steps:")
        print("  1. Create config.json from config_testing.json")
        print("  2. Run: python hundea_v3.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("\n📝 Troubleshooting:")
        print("  1. Read TROUBLESHOOTING.md")
        print("  2. Check huntdea_v3.log")
        print("  3. Verify internet connection")
        return 1


if __name__ == "__main__":
    sys.exit(main())
