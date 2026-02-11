"""
🧪 LOCAL TEST - Antes de GitHub Actions
────────────────────────────────────────

Test RÁPIDO local para verificar que los fixes funcionan
ANTES de hacer commit y push (que activa GitHub Actions).

Esto evita runs innecesarios en GitHub.
"""

import sys
print("\n" + "="*70)
print("🧪 LOCAL TEST - Pre-Commit Verification")
print("="*70)
print()

print("⚙️  Testing fixes...")
print()

# Test 1: Scoring module
print("1️⃣  Testing scoring.py (ConsoleDeal support)...")
try:
    from modules.core.scoring import SistemaScoring
    from modules.consoles.base_console_hunter import ConsoleDeal
    
    scoring = SistemaScoring()
    
    # Test with ConsoleDeal
    deal = ConsoleDeal(
        title="Test Game",
        store_url="https://example.com",
        platform="PlayStation",
        console_gen="PS5",
        original_price=60.0,
        current_price=20.0,
        discount_percent=67,
        game_id="test_123"
    )
    
    # Should not crash
    score = scoring.calcular_score(deal)
    print(f"   ✅ ConsoleDeal support: WORKING (score={score:.1f})")
    
    # Test with dict
    deal_dict = {
        'title': 'Test Game 2',
        'reviews_percent': 85,
        'reviews_count': 500
    }
    
    score2 = scoring.calcular_score(deal_dict)
    print(f"   ✅ Dict support: WORKING (score={score2:.1f})")
    
except Exception as e:
    print(f"   ❌ Scoring test FAILED: {e}")
    sys.exit(1)

print()

# Test 2: Ultra bot _score_deals
print("2️⃣  Testing hundea_v3_ultra.py (_score_deals)...")
try:
    from hundea_v3_ultra import HunDeaBotUltra
    
    # Create minimal config
    config = {
        'apis': {},
        'filters': {},
        'webhooks': {},
        'features': {
            'enable_ai_validation': False,
            'enable_parallel_fetch': False,
            'enable_advanced_scoring': True
        }
    }
    
    # Mock cache
    class MockCache:
        def is_posted(self, game_id):
            return False
        def cleanup_old_entries(self, days):
            pass
    
    # Temporarily create minimal bot
    import json
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config = f.name
    
    # Monkey patch cache
    import modules.core.cache_manager
    old_cache = modules.core.cache_manager.CacheManager
    modules.core.cache_manager.CacheManager = MockCache
    
    try:
        bot = HunDeaBotUltra(temp_config)
        
        # Test with mixed deals (dict + ConsoleDeal)
        test_deals = [
            {
                'title': 'Dict Game',
                'reviews_percent': 90,
                'source': 'steam'
            },
            ConsoleDeal(
                title="Console Game",
                store_url="https://example.com",
                platform="Xbox",
                console_gen="Xbox Series X",
                original_price=50.0,
                current_price=15.0,
                discount_percent=70,
                game_id="console_123"
            )
        ]
        
        # Should not crash
        scored = bot._score_deals(test_deals)
        
        print(f"   ✅ _score_deals: WORKING ({len(scored)} deals scored)")
        print(f"   ✅ Mixed types: Dict + ConsoleDeal OK")
        
    finally:
        # Restore
        modules.core.cache_manager.CacheManager = old_cache
        import os
        os.unlink(temp_config)
    
except Exception as e:
    print(f"   ❌ Ultra bot test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Final summary
print("="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70)
print()
print("✅ scoring.py: ConsoleDeal + Dict support working")
print("✅ hundea_v3_ultra.py: _score_deals fixed")
print()
print("💡 Next steps:")
print("   1. git add modules/core/scoring.py hundea_v3_ultra.py")
print("   2. git commit -m \"fix: Support ConsoleDeal in scoring system\"")
print("   3. git push")
print()
print("🚀 Ready for GitHub Actions!")
print("="*70)
print()
