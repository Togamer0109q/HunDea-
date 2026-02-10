"""
🧪 Quick Test - PlayStation Hunter FIXED
─────────────────────────────────────────

Test rápido del PlayStation hunter con el endpoint CORRECTO.

Author: HunDeaBot Team
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print("🧪 TESTING PLAYSTATION HUNTER - REAL API ENDPOINT")
print("="*70)
print()

# Import
from modules.consoles.playstation_hunter import test_playstation

# Run test
deals = test_playstation()

# Summary
print("\n" + "="*70)
print("📊 QUICK TEST SUMMARY")
print("="*70)

if deals and len(deals) > 0:
    print(f"\n✅ SUCCESS! Found {len(deals)} PlayStation deals")
    print(f"🏆 API endpoint is CORRECT!")
    print(f"\nNow run: python hundea_v3_ultimate.py")
else:
    print(f"\n⚠️  Found 0 deals")
    print(f"\nPossible reasons:")
    print(f"1. No current sales on PlayStation Store")
    print(f"2. API rate limit (500/hour)")
    print(f"3. Region 'us' has no deals right now")
    print(f"\nTry:")
    print(f"- Wait 5 minutes and retry")
    print(f"- Change region to 'gb' or 'eu' in config.json")

print("\n" + "="*70 + "\n")
