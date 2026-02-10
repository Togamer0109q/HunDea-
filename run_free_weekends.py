"""
🆓 Quick Free Weekends Runner - Standalone
───────────────────────────────────────────

Script rápido para ejecutar solo free weekends hunt.
Útil para testing o ejecución separada del bot principal.

Author: HunDeaBot Team
Version: 1.0.0
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.free_weekend_hunter import FreeWeekendHunter
from modules.free_weekend_notifier import FreeWeekendNotifier


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('free_weekends.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def load_config():
    """Load configuration from config.json."""
    config_path = Path('config.json')
    
    if not config_path.exists():
        print("⚠️  config.json not found, using defaults")
        return {
            'webhooks': {
                'free_weekends': None
            },
            'features': {
                'free_weekends': {
                    'enabled': True,
                    'platforms': ['steam', 'xbox', 'epic'],
                    'notify_upcoming': False
                }
            }
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main execution."""
    logger = setup_logging()
    
    print("\n" + "="*70)
    print("🆓 FREE WEEKENDS HUNTER - Standalone Runner")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Load config
    config = load_config()
    features = config.get('features', {}).get('free_weekends', {})
    
    # Check if enabled
    if not features.get('enabled', True):
        logger.warning("⚠️  Free weekends feature is disabled in config")
        return
    
    # Initialize hunter
    logger.info("🔧 Initializing Free Weekend Hunter...")
    hunter = FreeWeekendHunter(logger=logger)
    
    # Hunt for free weekends
    results = hunter.hunt_all_free_weekends()
    
    # Get totals
    total_games = sum(len(games) for games in results.values())
    active_games = sum(
        len([g for g in games if g.get('is_active', False)])
        for games in results.values()
    )
    
    print("\n" + "="*70)
    print("📊 RESULTS SUMMARY")
    print("="*70)
    print(f"🎮 Total games found: {total_games}")
    print(f"✅ Active now: {active_games}")
    print(f"🔜 Upcoming: {total_games - active_games}")
    
    # Display games
    for platform, games in results.items():
        if games:
            print(f"\n{platform.upper()} ({len(games)} games):")
            for game in games:
                status = "🟢 ACTIVE" if game.get('is_active') else "🔜 UPCOMING"
                print(f"  {status} {game['name']}")
                print(f"     📅 {game['start_date']} → {game['end_date']}")
    
    # Send to Discord if webhook configured
    webhook_url = config.get('webhooks', {}).get('free_weekends')
    
    if webhook_url and webhook_url != "YOUR_FREE_WEEKENDS_WEBHOOK_HERE":
        print("\n" + "="*70)
        print("📤 SENDING TO DISCORD")
        print("="*70)
        
        notifier = FreeWeekendNotifier(webhook_url, logger=logger)
        
        total_sent = 0
        
        for platform, games in results.items():
            # Filter based on config
            if features.get('notify_upcoming', False):
                games_to_send = games
            else:
                games_to_send = [g for g in games if g.get('is_active', False)]
            
            if games_to_send:
                logger.info(f"📤 Sending {len(games_to_send)} {platform} notifications...")
                sent = notifier.send_batch_notifications(games_to_send)
                total_sent += sent
        
        print(f"\n✅ Sent {total_sent}/{active_games} notifications to Discord")
    else:
        print("\n⚠️  No webhook configured - skipping Discord notifications")
        print("💡 Set 'webhooks.free_weekends' in config.json to enable")
    
    print("\n" + "="*70)
    print("✅ Free Weekends Hunt Complete!")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
