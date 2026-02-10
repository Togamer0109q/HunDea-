"""
🚀 HunDeaBot v3.0 ULTIMATE - All Hunters Edition
─────────────────────────────────────────────────

Bot mejorado que usa TODOS los hunters:
- PlayStation (PlatPrices API)
- Xbox (CheapShark fallback)
- Nintendo (CheapShark)
- Epic Games
- Steam (NEW!)
- GOG (NEW!)
- VR (NEW!)

Author: HunDeaBot Team
Version: 3.8.0 - ULTIMATE EDITION
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Console hunters
from modules.consoles import PlayStationHunter, XboxHunter, NintendoHunter

# PC hunters
from modules.epic_hunter import EpicHunter
from modules.steam_hunter import SteamHunter
from modules.gog_hunter import GOGHunter
from modules.gamerpower_hunter import GamerPowerHunter
from modules.ggdeals_hunter import GGDealsHunter

# VR hunter
from modules.vr_hunter import VRHunter

# Core
from modules.core.cache_manager import CacheManager
from modules.core.env_config import apply_env_overrides

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('hundea_ultimate.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HunDeaBotUltimate:
    """Bot ULTIMATE con todos los hunters."""
    
    def __init__(self, config_file='config.json'):
        """Initialize bot."""
        self.config = self._load_config(config_file)
        self.cache = CacheManager()
        
        logger.info("🚀 HunDeaBot v3.0 ULTIMATE initialized")
        logger.info(f"   📊 All hunters enabled")
    
    def _load_config(self, config_file):
        """Load config."""
        try:
            with open(config_file) as f:
                config = json.load(f)
                return apply_env_overrides(config, logger=logger)
        except:
            return apply_env_overrides({}, logger=logger)
    
    def run(self):
        """Execute ULTIMATE hunt."""
        logger.info("\n" + "="*70)
        logger.info("🚀 HUNDEABOT V3.0 ULTIMATE - ALL HUNTERS EDITION")
        logger.info("="*70)
        logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_deals = {}
        
        # ═══════════════════════════════════════════════════════
        # CONSOLE HUNTERS
        # ═══════════════════════════════════════════════════════
        
        logger.info("🎮 CONSOLE HUNTERS")
        logger.info("-"*70)
        
        # PlayStation
        try:
            logger.info("\n🟦 PlayStation Hunter...")
            ps = PlayStationHunter(self.config, self.cache, logger)
            deals = ps.fetch_deals()
            all_deals['playstation'] = len(deals)
            logger.info(f"✅ PlayStation: {len(deals)} deals")
        except Exception as e:
            logger.error(f"❌ PlayStation error: {e}")
            all_deals['playstation'] = 0
        
        # Xbox
        try:
            logger.info("\n🟩 Xbox Hunter...")
            xbox = XboxHunter(self.config, self.cache, logger)
            deals = xbox.fetch_deals()
            all_deals['xbox'] = len(deals)
            logger.info(f"✅ Xbox: {len(deals)} deals")
        except Exception as e:
            logger.error(f"❌ Xbox error: {e}")
            all_deals['xbox'] = 0
        
        # Nintendo
        try:
            logger.info("\n🟥 Nintendo Hunter...")
            nintendo = NintendoHunter(self.config, self.cache, logger)
            deals = nintendo.fetch_deals()
            all_deals['nintendo'] = len(deals)
            logger.info(f"✅ Nintendo: {len(deals)} deals")
        except Exception as e:
            logger.error(f"❌ Nintendo error: {e}")
            all_deals['nintendo'] = 0
        
        # ═══════════════════════════════════════════════════════
        # PC HUNTERS
        # ═══════════════════════════════════════════════════════
        
        logger.info("\n\n💻 PC HUNTERS")
        logger.info("-"*70)
        
        # Epic
        try:
            logger.info("\n⭐ Epic Games Hunter...")
            epic = EpicHunter(logger=logger)
            games = epic.obtener_juegos_gratis()
            all_deals['epic'] = len(games)
            logger.info(f"✅ Epic: {len(games)} free games")
        except Exception as e:
            logger.error(f"❌ Epic error: {e}")
            all_deals['epic'] = 0
        
        # Steam
        try:
            logger.info("\n💨 Steam Hunter...")
            steam = SteamHunter(logger=logger)
            games = steam.obtener_juegos_gratis()
            all_deals['steam'] = len(games)
            logger.info(f"✅ Steam: {len(games)} deals")
        except Exception as e:
            logger.error(f"❌ Steam error: {e}")
            all_deals['steam'] = 0
        
        # GOG
        try:
            logger.info("\n🟪 GOG Hunter...")
            gog = GOGHunter(logger=logger)
            games = gog.obtener_juegos_gratis()
            all_deals['gog'] = len(games)
            logger.info(f"✅ GOG: {len(games)} DRM-free deals")
        except Exception as e:
            logger.error(f"❌ GOG error: {e}")
            all_deals['gog'] = 0

        # GamerPower
        try:
            logger.info("\nGamerPower Hunter...")
            gp = GamerPowerHunter(logger=logger)
            games = gp.fetch_deals()
            all_deals['gamerpower'] = len(games)
            logger.info(f"OK GamerPower: {len(games)} giveaways")
        except Exception as e:
            logger.error(f"GamerPower error: {e}")
            all_deals['gamerpower'] = 0

        # GG.deals (bundles)
        try:
            logger.info("\nGG.deals Bundles Hunter...")
            gg = GGDealsHunter(logger=logger)
            games = gg.fetch_deals()
            all_deals['ggdeals'] = len(games)
            logger.info(f"OK GG.deals: {len(games)} bundles")
        except Exception as e:
            logger.error(f"GG.deals error: {e}")
            all_deals['ggdeals'] = 0
        
        # ═══════════════════════════════════════════════════════
        # VR HUNTER
        # ═══════════════════════════════════════════════════════
        
        logger.info("\n\n🥽 VR HUNTER")
        logger.info("-"*70)
        
        try:
            logger.info("\n🥽 VR Multi-Platform Hunter...")
            vr = VRHunter(logger=logger)
            games = vr.hunt_vr_deals()
            all_deals['vr'] = len(games)
            logger.info(f"✅ VR: {len(games)} deals across all platforms")
        except Exception as e:
            logger.error(f"❌ VR error: {e}")
            all_deals['vr'] = 0
        
        # ═══════════════════════════════════════════════════════
        # SUMMARY
        # ═══════════════════════════════════════════════════════
        
        logger.info("\n\n" + "="*70)
        logger.info("📊 ULTIMATE HUNT SUMMARY")
        logger.info("="*70)
        
        logger.info("\n🎮 CONSOLES:")
        logger.info(f"   PlayStation: {all_deals.get('playstation', 0)} deals")
        logger.info(f"   Xbox:        {all_deals.get('xbox', 0)} deals")
        logger.info(f"   Nintendo:    {all_deals.get('nintendo', 0)} deals")
        console_total = sum([all_deals.get('playstation', 0), 
                            all_deals.get('xbox', 0), 
                            all_deals.get('nintendo', 0)])
        
        logger.info("\n💻 PC:")
        logger.info(f"   Epic Games:  {all_deals.get('epic', 0)} deals")
        logger.info(f"   Steam:       {all_deals.get('steam', 0)} deals")
        logger.info(f"   GOG:         {all_deals.get('gog', 0)} deals")
        logger.info(f"   GamerPower:  {all_deals.get('gamerpower', 0)} deals")
        logger.info(f"   GG.deals:    {all_deals.get('ggdeals', 0)} deals")
        pc_total = sum([all_deals.get('epic', 0), 
                       all_deals.get('steam', 0), 
                       all_deals.get('gog', 0),
                       all_deals.get('gamerpower', 0),
                       all_deals.get('ggdeals', 0)])
        
        logger.info("\n🥽 VR:")
        logger.info(f"   All VR:      {all_deals.get('vr', 0)} deals")
        
        total = sum(all_deals.values())
        
        logger.info("\n" + "─"*70)
        logger.info(f"🎉 TOTAL DEALS: {total}")
        logger.info(f"   Consoles: {console_total}")
        logger.info(f"   PC:       {pc_total}")
        logger.info(f"   VR:       {all_deals.get('vr', 0)}")
        logger.info("="*70)
        
        # Working hunters
        working = sum(1 for v in all_deals.values() if v > 0)
        total_hunters = len(all_deals)
        
        logger.info(f"\n✅ Working hunters: {working}/{total_hunters}")
        
        if working == total_hunters:
            logger.info("🏆 ALL HUNTERS WORKING PERFECTLY!")
        elif working >= 4:
            logger.info("✅ Most hunters working well")
        else:
            logger.info("⚠️  Some hunters need attention")
        
        logger.info("\n" + "="*70)
        logger.info(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70 + "\n")
        
        return total


def main():
    """Main entry point."""
    try:
        bot = HunDeaBotUltimate()
        total = bot.run()
        
        if total == 0:
            logger.warning("\n⚠️  No deals found - check internet connection")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
