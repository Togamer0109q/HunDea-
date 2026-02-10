"""
🎮 HunDeaBot v3.0 - Professional Gaming Deals Hunter
────────────────────────────────────────────────────

Main coordinator script that orchestrates all hunters.
Executes console and PC hunters, filters deals, and sends Discord notifications.

Author: HunDeaBot Team
Version: 3.0.0
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Import console hunters
from modules.consoles import PlayStationHunter, XboxHunter, NintendoHunter, ConsoleDeal

# Import PC hunters (existing classes)
PC_HUNTERS_AVAILABLE = False
PC_HUNTER_ERROR = None
try:
    from modules.epic_hunter import EpicHunter
    from modules.cheapshark_hunter import CheapSharkHunter
    PC_HUNTERS_AVAILABLE = True
except ImportError as e:
    PC_HUNTER_ERROR = str(e)
    EpicHunter = None
    CheapSharkHunter = None

# Import notifiers
from modules.notifiers.console_notifier import ConsoleNotifier
from modules.status_notifier import StatusNotifier

# Import utilities
from modules.core.cache_manager import CacheManager
from modules.core.env_config import apply_env_overrides

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('huntdea_v3.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log PC hunters status
if PC_HUNTERS_AVAILABLE:
    logger.info("✅ PC hunters loaded successfully")
else:
    logger.warning(f"⚠️  PC hunters not fully available: {PC_HUNTER_ERROR}")
    logger.info("🎮 Console-only mode")


class HunDeaBot:
    """Main bot coordinator."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the bot."""
        self.config = self._load_config(config_file)
        self.cache = CacheManager()
        
        # Initialize notifiers
        self.console_notifier = ConsoleNotifier(self.config, logger)
        self.status_notifier = StatusNotifier(self.config, logger)
        
        # Get API keys
        self.rawg_api_key = self.config.get('apis', {}).get('rawg')
        
        # Features
        features = self.config.get('features', {})
        self.enable_console = features.get('enable_console_hunting', True)
        self.enable_pc = features.get('enable_pc_hunting', True)
        
        logger.info("🤖 HunDeaBot v3.0 initialized")
        logger.info(f"🎮 Console hunting: {'✅' if self.enable_console else '❌'}")
        logger.info(f"💻 PC hunting: {'✅' if self.enable_pc else '❌'}")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            logger.error(f"❌ Config file not found: {config_file}")
            logger.info("💡 Creating from example...")
            
            # Try to load example config
            example_path = Path('config_v3.example.json')
            if example_path.exists():
                with open(example_path, 'r') as f:
                    config = json.load(f)
                    return apply_env_overrides(config, logger=logger)
            
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config = apply_env_overrides(config, logger=logger)
                logger.info(f"✅ Loaded config from {config_file}")
                return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            sys.exit(1)
    
    def hunt_consoles(self) -> List[ConsoleDeal]:
        """Hunt for console deals across all platforms."""
        if not self.enable_console:
            logger.info("⏭️  Console hunting disabled")
            return []
        
        logger.info("\n" + "="*60)
        logger.info("🎮 Starting Console Hunt")
        logger.info("="*60)
        
        all_deals = []
        
        # PlayStation
        try:
            logger.info("\n🟦 Hunting PlayStation deals...")
            ps_hunter = PlayStationHunter(self.config, self.cache, logger)
            ps_deals = ps_hunter.hunt(self.rawg_api_key)
            all_deals.extend(ps_deals)
            logger.info(f"✅ PlayStation: {len(ps_deals)} deals found")
        except Exception as e:
            logger.error(f"❌ PlayStation hunt failed: {e}")
            self.console_notifier.send_status_message(
                "PlayStation", 
                f"Hunt failed: {str(e)}", 
                is_error=True
            )
        
        # Xbox
        try:
            logger.info("\n🟩 Hunting Xbox deals...")
            xbox_hunter = XboxHunter(self.config, self.cache, logger)
            xbox_deals = xbox_hunter.hunt(self.rawg_api_key)
            all_deals.extend(xbox_deals)
            logger.info(f"✅ Xbox: {len(xbox_deals)} deals found")
        except Exception as e:
            logger.error(f"❌ Xbox hunt failed: {e}")
            self.console_notifier.send_status_message(
                "Xbox", 
                f"Hunt failed: {str(e)}", 
                is_error=True
            )
        
        # Nintendo
        try:
            logger.info("\n🟥 Hunting Nintendo deals...")
            nintendo_hunter = NintendoHunter(self.config, self.cache, logger)
            nintendo_deals = nintendo_hunter.hunt(self.rawg_api_key)
            all_deals.extend(nintendo_deals)
            logger.info(f"✅ Nintendo: {len(nintendo_deals)} deals found")
        except Exception as e:
            logger.error(f"❌ Nintendo hunt failed: {e}")
            self.console_notifier.send_status_message(
                "Nintendo", 
                f"Hunt failed: {str(e)}", 
                is_error=True
            )
        
        logger.info(f"\n🎮 Console Hunt Complete: {len(all_deals)} total deals")
        return all_deals
    
    def hunt_pc(self) -> int:
        """Hunt for PC deals (using existing hunters)."""
        if not self.enable_pc or not PC_HUNTERS_AVAILABLE:
            if not self.enable_pc:
                logger.info("⏭️  PC hunting disabled")
            else:
                logger.info("⏭️  PC hunters not available")
            return 0
        
        logger.info("\n" + "="*60)
        logger.info("💻 Starting PC Hunt")
        logger.info("="*60)
        
        total_pc_deals = 0
        
        # Epic Games
        if EpicHunter:
            try:
                logger.info("\n⭐ Hunting Epic Games...")
                epic_hunter = EpicHunter()
                juegos_gratis = epic_hunter.obtener_juegos_gratis()
                
                # Nota: Los hunters PC tienen su propia lógica de envío
                # Por ahora solo contamos los juegos encontrados
                total_pc_deals += len(juegos_gratis)
                logger.info(f"✅ Epic: {len(juegos_gratis)} free games found")
            except Exception as e:
                logger.error(f"❌ Epic hunt failed: {e}")
        
        # CheapShark
        if CheapSharkHunter:
            try:
                logger.info("\n🦈 Hunting CheapShark deals...")
                cs_hunter = CheapSharkHunter()
                # Los hunters PC antiguos tienen diferentes interfaces
                # Se necesitaría adaptar cada uno según su estructura
                logger.info("ℹ️  CheapShark hunter available but needs integration")
            except Exception as e:
                logger.error(f"❌ CheapShark hunt failed: {e}")
        
        logger.info(f"\n💻 PC Hunt Complete: {total_pc_deals} deals found")
        logger.info("🔧 Note: PC hunters need webhook integration - coming soon")
        return total_pc_deals
    
    def run(self):
        """Main execution flow."""
        logger.info("\n" + "="*60)
        logger.info("🚀 HunDeaBot v3.0 - Professional Gaming Deals Hunter")
        logger.info("="*60)
        logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Cleanup old cache entries
            self.cache.cleanup_old_entries(days=30)
            
            total_console_deals = 0
            total_pc_deals = 0
            total_posted = 0
            
            # Hunt consoles
            console_deals = self.hunt_consoles()
            total_console_deals = len(console_deals)
            
            # Send console deals
            if console_deals:
                stats = self.console_notifier.send_deals(console_deals)
                # Mark as posted and count
                for deal in console_deals:
                    self.cache.add_to_cache(deal.game_id, deal.to_dict())
                    total_posted += 1
            
            # Hunt PC
            total_pc_deals = self.hunt_pc()
            
            # Final summary and Dashboard
            logger.info("\n" + "="*60)
            logger.info("📊 Hunt Summary")
            logger.info("="*60)
            logger.info(f"🎮 Console deals: {total_console_deals}")
            logger.info(f"💻 PC deals: {total_pc_deals}")
            logger.info(f"🎉 Total deals found: {total_console_deals + total_pc_deals}")
            logger.info(f"✅ Total deals posted: {total_posted}")
            logger.info("="*60)
            
            # Send status dashboard to Discord
            self.status_notifier.send_dashboard(
                deals_found=(total_console_deals + total_pc_deals),
                deals_posted=total_posted
            )
            
        except Exception as e:
            error_msg = f"Fatal error during run: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            self.status_notifier.send_error_report(error_msg)
            raise e


def main():
    """Main entry point."""
    try:
        bot = HunDeaBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
