"""
🧪 TEST ALL HUNTERS - Complete Verification
────────────────────────────────────────────

Tests ALL hunters and shows results:
- PlayStation (with API key)
- Xbox (CheapShark)
- Epic Games
- Steam
- GOG
- VR (SteamVR, Quest, Viveport)

Author: HunDeaBot Team
Version: 3.7.0 - COMPLETE TEST
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def test_all_hunters():
    """Test all hunters comprehensively."""
    
    print("\n" + "="*70)
    print("🧪 HUNDEABOT - COMPLETE HUNTER TEST")
    print("="*70)
    print("\nTesting ALL hunters to verify functionality...")
    print()
    
    results = {}
    
    # ═══════════════════════════════════════════════════════════
    # TEST 1: PLAYSTATION
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("🟦 TEST 1: PLAYSTATION HUNTER")
    print("-"*70)
    
    try:
        from modules.consoles.playstation_hunter import PlayStationHunter
        
        config = {
            'apis': {
                'platprices': {
                    'api_key': 'GH28jbaLCoVsQ5QINHnV8fHpvsQnuUbB',
                    'region': 'us',
                    'platform': 'ps5'
                }
            },
            'filters': {
                'playstation': {
                    'min_discount': 20,  # Only 20%+ to filter
                    'min_score': 0,
                    'exclude_dlc': False,
                    'max_price': 999999
                }
            }
        }
        
        class MockCache:
            def is_posted(self, game_id):
                return False
            def add_to_cache(self, game_id, data):
                pass
        
        hunter = PlayStationHunter(config, MockCache())
        deals = hunter.fetch_deals()
        
        results['playstation'] = len(deals)
        
        print(f"\n✅ PlayStation: {len(deals)} deals found")
        
        if deals:
            print("\n📋 Sample (first 5):")
            for i, deal in enumerate(deals[:5], 1):
                print(f"   {i}. {deal.title}")
                print(f"      ${deal.current_price:.2f} (was ${deal.original_price:.2f}) - {deal.discount_percent}% OFF")
        else:
            print("   ⚠️  No deals found (may be API issue or filters too strict)")
    
    except Exception as e:
        print(f"\n❌ PlayStation test failed: {e}")
        results['playstation'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # TEST 2: XBOX
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("🟩 TEST 2: XBOX HUNTER")
    print("-"*70)
    
    try:
        from modules.consoles.xbox_hunter import XboxHunter
        
        config = {
            'apis': {},
            'filters': {
                'xbox': {
                    'min_discount': 20,
                    'min_score': 0,
                    'exclude_dlc': False,
                    'max_price': 999999
                }
            }
        }
        
        hunter = XboxHunter(config, MockCache())
        deals = hunter.fetch_deals()
        
        results['xbox'] = len(deals)
        
        print(f"\n✅ Xbox: {len(deals)} deals found")
        
        if deals:
            print("\n📋 Sample (first 5):")
            for i, deal in enumerate(deals[:5], 1):
                print(f"   {i}. {deal.title}")
                print(f"      ${deal.current_price:.2f} (was ${deal.original_price:.2f}) - {deal.discount_percent}% OFF")
    
    except Exception as e:
        print(f"\n❌ Xbox test failed: {e}")
        results['xbox'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # TEST 3: EPIC GAMES
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("⭐ TEST 3: EPIC GAMES HUNTER")
    print("-"*70)
    
    try:
        from modules.epic_hunter import EpicHunter
        
        hunter = EpicHunter()
        games = hunter.obtener_juegos_gratis()
        
        results['epic'] = len(games)
        
        print(f"\n✅ Epic Games: {len(games)} free games found")
        
        if games:
            print("\n📋 Free Games:")
            for i, game in enumerate(games, 1):
                # Epic returns different key formats
                title = game.get('title') or game.get('name') or game.get('titulo') or 'Unknown'
                print(f"   {i}. {title}")
                if 'description' in game:
                    desc = game['description'][:60]
                    print(f"      {desc}...")
    
    except Exception as e:
        print(f"\n❌ Epic test failed: {e}")
        results['epic'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # TEST 4: STEAM
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("💨 TEST 4: STEAM HUNTER")
    print("-"*70)
    
    try:
        from modules.steam_hunter import SteamHunter
        
        hunter = SteamHunter()
        deals = hunter.obtener_juegos_gratis()
        
        results['steam'] = len(deals)
        
        print(f"\n✅ Steam: {len(deals)} deals found")
        
        if deals:
            print("\n📋 Sample (first 5):")
            for i, deal in enumerate(deals[:5], 1):
                print(f"   {i}. {deal['title']}")
                if deal['discount_percent'] > 0:
                    print(f"      ${deal['price']:.2f} (was ${deal['regular_price']:.2f}) - {deal['discount_percent']}% OFF")
                else:
                    print(f"      FREE")
    
    except Exception as e:
        print(f"\n❌ Steam test failed: {e}")
        results['steam'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # TEST 5: GOG
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("🟪 TEST 5: GOG HUNTER")
    print("-"*70)
    
    try:
        from modules.gog_hunter import GOGHunter
        
        hunter = GOGHunter()
        deals = hunter.obtener_juegos_gratis()
        
        results['gog'] = len(deals)
        
        print(f"\n✅ GOG: {len(deals)} deals found")
        
        if deals:
            print("\n📋 Sample (first 5):")
            for i, deal in enumerate(deals[:5], 1):
                print(f"   {i}. {deal['title']}")
                print(f"      ${deal['price']:.2f} (was ${deal['regular_price']:.2f}) - {deal['discount_percent']}% OFF")
                print(f"      🔓 DRM-Free")
    
    except Exception as e:
        print(f"\n❌ GOG test failed: {e}")
        results['gog'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # TEST 6: VR
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("🥽 TEST 6: VR HUNTER")
    print("-"*70)
    
    try:
        from modules.vr_hunter import VRHunter
        
        hunter = VRHunter()
        deals = hunter.hunt_vr_deals()
        
        results['vr'] = len(deals)
        
        print(f"\n✅ VR: {len(deals)} deals found")
        
        if deals:
            print("\n📋 Sample (first 5):")
            for i, deal in enumerate(deals[:5], 1):
                emoji = hunter.get_platform_emoji(deal.get('vr_platform', ''))
                print(f"   {i}. {emoji} {deal['title']}")
                print(f"      Platform: {deal.get('vr_platform', 'Unknown')}")
                if deal.get('discount_percent', 0) > 0:
                    print(f"      ${deal['current_price']:.2f} (was ${deal['original_price']:.2f}) - {deal['discount_percent']}% OFF")
    
    except Exception as e:
        print(f"\n❌ VR test failed: {e}")
        results['vr'] = 0
    
    # ═══════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    total_deals = sum(results.values())
    
    print(f"\n🎮 CONSOLE HUNTERS:")
    print(f"   PlayStation: {results.get('playstation', 0)} deals")
    print(f"   Xbox:        {results.get('xbox', 0)} deals")
    
    print(f"\n💻 PC HUNTERS:")
    print(f"   Epic Games:  {results.get('epic', 0)} deals")
    print(f"   Steam:       {results.get('steam', 0)} deals")
    print(f"   GOG:         {results.get('gog', 0)} deals")
    
    print(f"\n🥽 VR HUNTERS:")
    print(f"   VR Total:    {results.get('vr', 0)} deals")
    
    print(f"\n" + "─"*70)
    print(f"🎉 TOTAL DEALS FOUND: {total_deals}")
    print("="*70)
    
    # Status check
    print("\n✅ STATUS CHECK:")
    
    working = sum(1 for v in results.values() if v > 0)
    total_hunters = len(results)
    
    print(f"   Working hunters: {working}/{total_hunters}")
    
    if working == total_hunters:
        print("   🏆 ALL HUNTERS WORKING!")
    elif working >= total_hunters * 0.5:
        print("   ⚠️  Some hunters need attention")
    else:
        print("   ❌ Multiple hunters failing")
    
    print("\n💡 TIPS:")
    
    if results.get('playstation', 0) == 0:
        print("   - PlayStation: Check API key or try different region")
    
    if results.get('xbox', 0) == 0:
        print("   - Xbox: CheapShark may be rate-limited, try again later")
    
    if total_deals < 20:
        print("   - Low deals: This may be normal in test environment")
        print("   - On production with internet: expect 100-200+ deals")
    
    print("\n" + "="*70)
    print()


if __name__ == "__main__":
    test_all_hunters()
