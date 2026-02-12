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

# Import console hunters
from modules.consoles import ConsoleDeal

# Import utilities
from modules.core.cache_manager import CacheManager
from modules.notifiers.console_notifier import ConsoleNotifier
from modules.notifiers.pc_notifier import PCNotifier
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
        
        # Initialize notifiers (v3 compatible only)
        try:
            self.console_notifier = ConsoleNotifier(self.config, logger)
            self.pc_notifier = PCNotifier(self.config, logger)
            logger.info("✅ Discord notifiers initialized")
            
            # Log webhook status
            webhooks = self.config.get('webhooks', {})
            logger.info("⚙️  Webhook Configuration:")
            for platform in ['playstation', 'xbox', 'nintendo', 'pc_deals', 'pc_premium', 'pc_weekends']:
                webhook = webhooks.get(platform, '')
                if webhook and 'YOUR_' not in webhook and webhook.startswith('https://'):
                    logger.info(f"   ✅ {platform}: Configured")
                elif webhook:
                    logger.warning(f"   ⚠️  {platform}: Invalid/Placeholder")
                else:
                    logger.warning(f"   ❌ {platform}: Not configured")
        except Exception as e:
            logger.error(f"❌ Discord notifiers failed: {e}", exc_info=True)
            self.console_notifier = None
            self.pc_notifier = None
        
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
        if new_deals and (self.console_notifier or self.pc_notifier):
            self._send_notifications(new_deals)
        elif not new_deals:
            logger.info("\n⚠️  No new deals to notify (all in cache)")
            logger.info("   💡 TIP: Delete cache.json to force re-notification")
        elif not (self.console_notifier or self.pc_notifier):
            logger.warning("\n⚠️  No notifiers available - cannot send notifications")
        
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
            
            # Only add score to dicts (ConsoleDeal has computed quality_score property)
            if isinstance(deal, dict):
                deal['quality_score'] = score
            # For ConsoleDeal objects, quality_score is already computed - don't modify
            
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
        logger.info(f"   Console notifier: {'✅ Available' if self.console_notifier else '❌ Not available'}")
        logger.info(f"   PC notifier: {'✅ Available' if self.pc_notifier else '❌ Not available'}")
        
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
                count = len(platform_deals)
                logger.info(f"   {platform}: {count} deals")
                
                # Console deals
                if platform in ['playstation', 'xbox', 'nintendo']:
                    logger.info(f"   → Console platform: {platform}")
                    if self.console_notifier:
                        logger.info(f"   → Converting {len(platform_deals)} deals to ConsoleDeal...")
                        # Convert to ConsoleDeal objects
                        console_deals = []
                        for d in platform_deals:
                            cd = self._convert_to_console_deal(d, platform)
                            if cd:
                                console_deals.append(cd)
                        
                        if console_deals:
                            logger.info(f"   → Sending {len(console_deals)} console deals to Discord...")
                            result = self.console_notifier.send_deals(console_deals)
                            logger.info(f"   → Result: {result}")
                        else:
                            logger.warning(f"   ⚠️  No valid console deals to send")
                    else:
                        logger.warning("⚠️  Console notifier not available")
                
                # PC deals
                else:
                    logger.info(f"   → PC platform: {platform}")
                    if self.pc_notifier:
                        # Iterate and send one by one to allow for channel routing
                        sent_count = 0
                        for deal in platform_deals:
                            # The new notifier handles routing based on score
                            if self.pc_notifier.send_deal(deal):
                                sent_count += 1
                        logger.info(f"   → Sent {sent_count}/{len(platform_deals)} PC deals to Discord.")
                    else:
                        logger.warning("⚠️  PC notifier not available")
        
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")

    def _convert_to_console_deal(self, deal, platform: str) -> 'ConsoleDeal':
        """Convert a deal dictionary/object to ConsoleDeal."""
        try:
            if isinstance(deal, ConsoleDeal):
                return deal
            
            # Extract fields from dict or object
            if isinstance(deal, dict):
                title = deal.get('title') or deal.get('name', 'Unknown')
                url = deal.get('url') or deal.get('store_url', '')
                price = deal.get('current_price') or deal.get('price', 0.0)
                original = deal.get('original_price') or deal.get('regular_price', price)
                discount = deal.get('discount_percent') or deal.get('discount', 0)
                console_gen = deal.get('console_gen') or platform
                game_id = deal.get('game_id') or deal.get('id')
                quality_score = deal.get('quality_score', 0)
            else:
                title = getattr(deal, 'title', 'Unknown')
                url = getattr(deal, 'url', getattr(deal, 'store_url', ''))
                price = getattr(deal, 'current_price', getattr(deal, 'price', 0.0))
                original = getattr(deal, 'original_price', getattr(deal, 'regular_price', price))
                discount = getattr(deal, 'discount_percent', getattr(deal, 'discount', 0))
                console_gen = getattr(deal, 'console_gen', platform)
                game_id = getattr(deal, 'game_id', getattr(deal, 'id', None))
                quality_score = getattr(deal, 'quality_score', 0)

            # Fix platform name for ConsoleDeal
            platform_map = {
                'playstation': 'PlayStation',
                'xbox': 'Xbox', 
                'nintendo': 'Nintendo'
            }
            clean_platform = platform_map.get(platform.lower(), 'PlayStation')
            
            # Create ConsoleDeal
            cd = ConsoleDeal(
                title=title,
                store_url=url,
                platform=clean_platform,
                console_gen=console_gen,
                original_price=float(original) if original else 0.0,
                current_price=float(price) if price else 0.0,
                discount_percent=int(discount) if discount else 0,
                game_id=game_id or f"{platform}_{title.replace(' ', '_')}"
            )
            
            # Restore score if available (ConsoleDeal computes it, but we might want the aggregated one)
            if quality_score:
                # We can't easily override the property, but we can set components
                # or just rely on re-computation if we have metadata
                pass
                
            return cd
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to convert deal to ConsoleDeal: {e}")
            return None

    
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
