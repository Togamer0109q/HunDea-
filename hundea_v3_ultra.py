"""
🚀 HunDeaBot v3 ULTRA - Maximum Power Edition
──────────────────────────────────────────────

EL BOT MÁS PODEROSO DEL UNIVERSO con:
✅ 15+ fuentes de deals
✅ AI validation anti-fake
✅ Multi-source deduplication
✅ Console + PC integration
✅ Review aggregation
✅ Advanced scoring
✅ Price history tracking
✅ Free weekends detection
✅ Real-time stats dashboard

Author: HunDeaBot Team
Version: 3.5.0 LEGENDARY ULTRA MEGA PRO EDITION
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Import mega aggregator
from modules.mega_api_aggregator import MegaAPIAggregator

# Import AI
from modules.ai import SmartDealValidator

# Import utilities
from modules.core.cache_manager import CacheManager
from modules.discord_notifier import DiscordNotifier
from modules.scoring import SistemaScoring
from modules.core.env_config import apply_env_overrides

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hundea_v3_ultra.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HunDeaBotUltra:
    """
    HunDeaBot v3 ULTRA - Maximum power edition.
    """
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the ULTRA bot."""
        self.config = self._load_config(config_file)
        self.cache = CacheManager()
        
        # Initialize mega aggregator
        self.aggregator = MegaAPIAggregator(
            self.config,
            self.cache,
            logger
        )
        
        # Initialize scoring system
        self.scoring = SistemaScoring(logger=logger)
        
        # Initialize notifier
        try:
            self.notifier = DiscordNotifier(self.config, logger)
            logger.info("✅ Discord notifier initialized")
        except Exception as e:
            logger.warning(f"⚠️  Discord notifier failed: {e}")
            self.notifier = None
        
        # Features
        features = self.config.get('features', {})
        self.use_ai = features.get('enable_ai_validation', True)
        self.use_parallel = features.get('enable_parallel_fetch', True)
        self.use_scoring = features.get('enable_advanced_scoring', True)
        
        logger.info("🚀 HunDeaBot v3 ULTRA initialized")
        logger.info(f"   🧠 AI Validation: {'ON' if self.use_ai else 'OFF'}")
        logger.info(f"   ⚡ Parallel Fetch: {'ON' if self.use_parallel else 'OFF'}")
        logger.info(f"   📊 Advanced Scoring: {'ON' if self.use_scoring else 'OFF'}")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            logger.error(f"❌ Config not found: {config_file}")
            logger.info("💡 Creating from example...")
            
            example = Path('config_v3.example.json')
            if example.exists():
                with open(example) as f:
                    config = json.load(f)
                    return apply_env_overrides(config, logger=logger)
            
            sys.exit(1)
        
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
            config = apply_env_overrides(config, logger=logger)
            logger.info(f"✅ Loaded config from {config_file}")
            return config
    
    def run(self):
        """Execute ULTRA MEGA HUNT."""
        logger.info("\n" + "="*80)
        logger.info("🚀 HUNDEABOT V3 ULTRA - MAXIMUM POWER EDITION")
        logger.info("="*80)
        logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Cleanup old cache
        self.cache.cleanup_old_entries(days=30)
        
        # Execute MEGA HUNT
        deals = self.aggregator.mega_hunt(
            use_ai=self.use_ai,
            parallel=self.use_parallel
        )
        
        # Apply scoring
        if self.use_scoring:
            deals = self._score_deals(deals)
        
        # Filter new deals
        new_deals = self._filter_new_deals(deals)
        
        # Send notifications
        if new_deals and self.notifier:
            self._send_notifications(new_deals)
        
        # Save to cache
        for deal in new_deals:
            game_id = self._get_game_id(deal)
            self.cache.add_to_cache(game_id, self._deal_to_dict(deal))
        
        # Final summary
        self._print_summary(deals, new_deals)
        
        logger.info(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
    
    def _score_deals(self, deals: List[Dict]) -> List[Dict]:
        """Apply advanced scoring to deals."""
        logger.info("\n📊 Applying advanced scoring...")
        
        scored = []
        for deal in deals:
            # Calculate score
            score = self.scoring.calcular_score(deal)
            
            # Add to deal
            if isinstance(deal, dict):
                deal['quality_score'] = score
            else:
                deal.quality_score = score
            
            scored.append(deal)
        
        # Sort by score
        scored.sort(
            key=lambda d: d.get('quality_score', 0) if isinstance(d, dict) else getattr(d, 'quality_score', 0),
            reverse=True
        )
        
        logger.info(f"✅ Scored {len(scored)} deals")
        
        return scored
    
    def _filter_new_deals(self, deals: List[Dict]) -> List[Dict]:
        """Filter out already posted deals."""
        new_deals = []
        
        for deal in deals:
            game_id = self._get_game_id(deal)
            
            if not self.cache.is_posted(game_id):
                new_deals.append(deal)
        
        logger.info(f"🆕 New deals: {len(new_deals)}/{len(deals)}")
        
        return new_deals
    
    def _get_game_id(self, deal) -> str:
        """Get unique game ID."""
        if isinstance(deal, dict):
            title = deal.get('title') or deal.get('name') or 'unknown'
            source = deal.get('source', 'unknown')
        else:
            title = getattr(deal, 'title', 'unknown')
            source = getattr(deal, 'source', 'unknown')
        
        normalized = self.aggregator._normalize_title(title)
        return f"{source}_{normalized}"
    
    def _deal_to_dict(self, deal) -> Dict:
        """Convert deal to dict for caching."""
        if isinstance(deal, dict):
            return deal
        else:
            return {
                'title': getattr(deal, 'title', ''),
                'source': getattr(deal, 'source', ''),
                'posted_at': datetime.now().isoformat()
            }
    
    def _send_notifications(self, deals: List[Dict]):
        """Send Discord notifications."""
        logger.info(f"\n📤 Sending {len(deals)} notifications...")
        
        try:
            # Group by platform
            by_platform = {}
            
            for deal in deals:
                platform = self._get_platform(deal)
                
                if platform not in by_platform:
                    by_platform[platform] = []
                
                by_platform[platform].append(deal)
            
            # Send by platform
            for platform, platform_deals in by_platform.items():
                logger.info(f"   {platform}: {len(platform_deals)} deals")
                # TODO: Send via notifier
        
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")
    
    def _get_platform(self, deal) -> str:
        """Get platform from deal."""
        if isinstance(deal, dict):
            source = deal.get('source', 'pc')
        else:
            source = getattr(deal, 'source', 'pc')
        
        # Map source to platform
        console_sources = ['playstation', 'xbox', 'nintendo']
        
        if source in console_sources:
            return source
        else:
            return 'pc'
    
    def _print_summary(self, all_deals: List[Dict], new_deals: List[Dict]):
        """Print execution summary."""
        stats = self.aggregator.get_stats()
        
        logger.info("\n" + "="*80)
        logger.info("📊 ULTRA HUNT SUMMARY")
        logger.info("="*80)
        logger.info(f"Sources queried:      {stats['total_sources']}")
        logger.info(f"Successful:           {stats['successful_sources']}")
        logger.info(f"Failed:               {stats['failed_sources']}")
        logger.info(f"Raw deals found:      {stats['total_deals_found']}")
        logger.info(f"After deduplication:  {stats['after_dedup']}")
        logger.info(f"After AI review:      {stats['after_ai_filter']}")
        logger.info(f"Suspicious flagged:   {stats['flagged_suspicious']}")
        logger.info(f"Total unique deals:   {len(all_deals)}")
        logger.info(f"New deals (posted):   {len(new_deals)}")
        logger.info("="*80)


def main():
    """Main entry point."""
    try:
        bot = HunDeaBotUltra()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
