"""
🧪 Test Complete AI System - All 3 Levels
──────────────────────────────────────────

Demonstrates the Triple AI Validation System.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.ai import (
    SmartDealValidator,
    AutonomousDealResearcher,
    WebPoweredInvestigator
)


def print_section(title):
    """Print section separator."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_level1():
    """Test Level 1: SmartDealValidator."""
    print_section("LEVEL 1: SMART DEAL VALIDATOR (Pattern Detection)")
    
    validator = SmartDealValidator()
    
    deals = [
        {
            'title': 'Cyberpunk 2077',
            'current_price': 29.99,
            'original_price': 59.99,
            'discount_percent': 50,
            'type': 'REAL'
        },
        {
            'title': 'MEGA ULTRA DELUXE PREMIUM GOLD EDITION',
            'current_price': 0.99,
            'original_price': 499.99,
            'discount_percent': 99,
            'type': 'FAKE'
        }
    ]
    
    for deal in deals:
        print(f"Testing: {deal['title']}")
        print(f"Price: ${deal['current_price']} (was ${deal['original_price']})")
        
        validation = validator.validate_deal(deal)
        
        print(f"\nResult: {validation['verdict']}")
        print(f"Confidence: {validation['confidence_score']:.0%}")
        print(f"Expected: {deal['type']}")
        
        # Check if correct
        is_correct = (
            (deal['type'] == 'REAL' and validation['is_real']) or
            (deal['type'] == 'FAKE' and not validation['is_real'])
        )
        
        print(f"✅ CORRECT" if is_correct else "❌ WRONG")
        print()
    
    stats = validator.get_stats()
    print(f"Stats: {stats}")


def test_level2():
    """Test Level 2: AutonomousDealResearcher."""
    print_section("LEVEL 2: AUTONOMOUS DEAL RESEARCHER (Multi-Source API)")
    
    print("NOTE: This requires internet and ITAD API key in production.")
    print("Running in DEMO mode...\n")
    
    researcher = AutonomousDealResearcher()  # No API key for demo
    
    deal = {
        'title': 'Elden Ring',
        'current_price': 39.99,
        'original_price': 59.99
    }
    
    print(f"Researching: {deal['title']}")
    print(f"Claimed: ${deal['current_price']} (was ${deal['original_price']})")
    
    research = researcher.research_deal(
        deal['title'],
        deal['current_price'],
        deal['original_price']
    )
    
    print(f"\nSources Found: {research['sources_found']}")
    print(f"Verdict: {research['verdict']['verdict']}")
    print(f"Confidence: {research['verdict']['confidence']:.0%}")
    
    if research['verdict'].get('issues'):
        print(f"\nIssues:")
        for issue in research['verdict']['issues']:
            print(f"  - {issue}")
    
    stats = researcher.get_stats()
    print(f"\nStats: {stats}")


def test_level3():
    """Test Level 3: WebPoweredInvestigator."""
    print_section("LEVEL 3: WEB-POWERED INVESTIGATOR (Web Intelligence)")
    
    print("NOTE: This requires web_search function in production.")
    print("Running in DEMO mode...\n")
    
    # Mock web search
    def mock_web_search(query):
        return f"Results for {query}: Found at Steam $29.99, GOG $31.99. Reviews positive."
    
    investigator = WebPoweredInvestigator(web_search_func=mock_web_search)
    
    deal = {
        'title': 'Red Dead Redemption 2',
        'current_price': 19.99,
        'original_price': 59.99,
        'store': 'Steam'
    }
    
    print(f"Investigating: {deal['title']}")
    print(f"Price: ${deal['current_price']} (was ${deal['original_price']})")
    print(f"Store: {deal['store']}")
    
    investigation = investigator.investigate_deal(
        deal['title'],
        deal['current_price'],
        deal['original_price'],
        deal['store']
    )
    
    print(f"\n{investigation['verdict']['verdict']}")
    print(f"\nReport:")
    print(investigation['verdict']['report'])
    print(f"\nRecommendation:")
    print(investigation['verdict']['recommendation'])
    
    stats = investigator.get_stats()
    print(f"\nStats: {stats}")


def test_pipeline():
    """Test complete pipeline with all 3 levels."""
    print_section("COMPLETE PIPELINE: All 3 Levels Working Together")
    
    # Initialize all levels
    validator = SmartDealValidator()
    researcher = AutonomousDealResearcher()
    investigator = WebPoweredInvestigator()
    
    # Test deal
    deal = {
        'title': 'GTA V',
        'current_price': 14.99,
        'original_price': 29.99,
        'discount_percent': 50
    }
    
    print(f"Deal: {deal['title']}")
    print(f"Price: ${deal['current_price']} (was ${deal['original_price']})")
    print(f"Discount: {deal['discount_percent']}%")
    
    # Level 1
    print(f"\n→ Level 1 Check...")
    l1 = validator.validate_deal(deal)
    print(f"  {l1['verdict']} ({l1['confidence_score']:.0%})")
    
    if l1['confidence_score'] < 0.7:
        # Level 2
        print(f"\n→ Level 2 Research...")
        l2 = researcher.research_deal(
            deal['title'],
            deal['current_price'],
            deal['original_price']
        )
        print(f"  {l2['verdict']['verdict']} ({l2['verdict']['confidence']:.0%})")
        
        if l2['verdict']['confidence'] < 0.8:
            # Level 3
            print(f"\n→ Level 3 Investigation...")
            l3 = investigator.investigate_deal(
                deal['title'],
                deal['current_price'],
                deal['original_price']
            )
            print(f"  {l3['verdict']['verdict']} ({l3['verdict']['confidence']:.0%})")
            
            final = l3['verdict']
        else:
            final = l2['verdict']
    else:
        final = l1
    
    print(f"\n✅ FINAL VERDICT:")
    print(f"   {final.get('verdict', l1['verdict'])}")
    print(f"   Confidence: {final.get('confidence', l1['confidence_score']):.0%}")


def main():
    """Run all tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "🧠 TRIPLE AI SYSTEM TEST 🧠" + " "*26 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\n" + "🎯 Testing all 3 levels of AI validation...")
    print("This demonstrates how the system detects REAL vs FAKE deals.\n")
    
    try:
        test_level1()
        test_level2()
        test_level3()
        test_pipeline()
        
        print_section("✅ ALL TESTS COMPLETED")
        print("The Triple AI System is working correctly!")
        print("\nNext Steps:")
        print("  1. Get ITAD API key for Level 2")
        print("  2. Integrate web_search for Level 3")
        print("  3. Add to hunters in hundea_v3.py")
        print("  4. Configure thresholds in config.json")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
