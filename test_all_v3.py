"""
🧪 HunDeaBot v3.0 - Test Suite
───────────────────────────────

Comprehensive tests for all console hunters.
Run this to verify everything works before deploying.

Author: HunDeaBot Team
Version: 3.0.0
"""

import json
import sys
from pathlib import Path


class MockCache:
    """Mock cache for testing."""
    
    def __init__(self):
        self.posted = set()
    
    def is_posted(self, game_id):
        return game_id in self.posted
    
    def add_to_cache(self, game_id, data):
        self.posted.add(game_id)


def test_playstation():
    """Test PlayStation hunter."""
    print("\n" + "="*60)
    print("🟦 Testing PlayStation Hunter")
    print("="*60)
    
    try:
        from modules.consoles.playstation_hunter import PlayStationHunter
        
        config = {
            'apis': {
                'psprices': {
                    'region': 'us',
                    'platform': 'ps5'
                }
            },
            'filters': {
                'playstation': {
                    'min_discount': 50,
                    'min_score': 3.5,
                    'exclude_dlc': True,
                    'include_ps_plus': True,
                    'max_price': 60
                }
            }
        }
        
        cache = MockCache()
        hunter = PlayStationHunter(config, cache)
        
        print("\n🔍 Fetching PlayStation deals...")
        deals = hunter.hunt()
        
        print(f"\n✅ Test Passed!")
        print(f"📊 Found {len(deals)} PlayStation deals")
        
        if deals:
            print(f"\n📋 Sample Deals (showing top 3):")
            for i, deal in enumerate(deals[:3], 1):
                print(f"\n{i}. {deal.title}")
                print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
                print(f"   📊 {deal.discount_percent}% off")
                print(f"   ⭐ Quality: {deal.quality_score:.1f}/5.0")
                print(f"   🎮 Platform: {deal.console_gen}")
                if deal.is_ps_plus:
                    print(f"   ➕ PS Plus Exclusive")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_xbox():
    """Test Xbox hunter."""
    print("\n" + "="*60)
    print("🟩 Testing Xbox Hunter")
    print("="*60)
    
    try:
        from modules.consoles.xbox_hunter import XboxHunter
        
        config = {
            'apis': {
                'xbox': {
                    'region': 'us',
                    'language': 'en-US'
                }
            },
            'filters': {
                'xbox': {
                    'min_discount': 50,
                    'min_score': 3.5,
                    'exclude_dlc': True,
                    'include_game_pass': True,
                    'max_price': 60
                }
            }
        }
        
        cache = MockCache()
        hunter = XboxHunter(config, cache)
        
        print("\n🔍 Fetching Xbox deals...")
        deals = hunter.hunt()
        
        print(f"\n✅ Test Passed!")
        print(f"📊 Found {len(deals)} Xbox deals")
        
        if deals:
            print(f"\n📋 Sample Deals (showing top 3):")
            for i, deal in enumerate(deals[:3], 1):
                print(f"\n{i}. {deal.title}")
                print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
                print(f"   📊 {deal.discount_percent}% off")
                print(f"   ⭐ Quality: {deal.quality_score:.1f}/5.0")
                print(f"   🎮 Platform: {deal.console_gen}")
                if deal.is_game_pass:
                    print(f"   🎮 Game Pass Available")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nintendo():
    """Test Nintendo hunter."""
    print("\n" + "="*60)
    print("🟥 Testing Nintendo Hunter")
    print("="*60)
    
    try:
        from modules.consoles.nintendo_hunter import NintendoHunter
        
        config = {
            'apis': {
                'dekudeals': {
                    'region': 'us'
                }
            },
            'filters': {
                'nintendo': {
                    'min_discount': 40,
                    'min_score': 3.5,
                    'exclude_dlc': True,
                    'indie_highlights': True,
                    'max_price': 60
                }
            }
        }
        
        cache = MockCache()
        hunter = NintendoHunter(config, cache)
        
        print("\n🔍 Fetching Nintendo deals...")
        deals = hunter.hunt()
        
        print(f"\n✅ Test Passed!")
        print(f"📊 Found {len(deals)} Nintendo deals")
        
        if deals:
            print(f"\n📋 Sample Deals (showing top 3):")
            for i, deal in enumerate(deals[:3], 1):
                print(f"\n{i}. {deal.title}")
                print(f"   💰 ${deal.current_price:.2f} (was ${deal.original_price:.2f})")
                print(f"   📊 {deal.discount_percent}% off")
                print(f"   ⭐ Quality: {deal.quality_score:.1f}/5.0")
                print(f"   🎮 Platform: {deal.console_gen}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notifier():
    """Test Discord notifier (dry run)."""
    print("\n" + "="*60)
    print("📱 Testing Discord Notifier")
    print("="*60)
    
    try:
        from modules.notifiers.console_notifier import ConsoleNotifier
        from modules.consoles.base_console_hunter import ConsoleDeal
        
        config = {
            'webhooks': {
                'playstation': None,  # Dry run
                'xbox': None,
                'nintendo': None
            },
            'roles': {
                'playstation': None,
                'xbox': None,
                'nintendo': None
            }
        }
        
        notifier = ConsoleNotifier(config)
        
        # Create sample deal
        sample_deal = ConsoleDeal(
            title="Test Game",
            store_url="https://example.com",
            platform="PlayStation",
            console_gen="PS5",
            original_price=69.99,
            current_price=34.99,
            discount_percent=50,
            currency="USD",
            game_id="test_001",
            genre="Action",
            metacritic_score=90,
            user_score=4.5
        )
        
        # Generate embed (no send)
        embed = notifier.create_deal_embed(sample_deal)
        
        print("\n✅ Test Passed!")
        print(f"📊 Generated embed for: {sample_deal.title}")
        print(f"🎨 Embed preview:")
        print(f"   Title: {embed['title']}")
        print(f"   Color: #{embed['color']:06X}")
        print(f"   Fields: {len(embed['fields'])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("⚙️ Testing Configuration")
    print("="*60)
    
    config_files = ['config.json', 'config_v3.example.json']
    
    for config_file in config_files:
        config_path = Path(config_file)
        
        if not config_path.exists():
            print(f"⚠️  {config_file} not found (optional)")
            continue
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"\n✅ {config_file} loaded successfully")
            
            # Validate structure
            required_keys = ['webhooks', 'apis', 'filters']
            for key in required_keys:
                if key not in config:
                    print(f"⚠️  Missing key: {key}")
                else:
                    print(f"   ✅ {key}: OK")
            
        except Exception as e:
            print(f"\n❌ Failed to load {config_file}: {e}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 HunDeaBot v3.0 - Test Suite")
    print("="*60)
    print("Running comprehensive tests...")
    
    results = {
        'Configuration': test_config(),
        'PlayStation Hunter': test_playstation(),
        'Xbox Hunter': test_xbox(),
        'Nintendo Hunter': test_nintendo(),
        'Discord Notifier': test_notifier()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n📈 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to deploy!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
