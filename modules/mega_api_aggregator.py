"""
🚀 MEGA API AGGREGATOR - Ultra Pro Edition
──────────────────────────────────────────

Agregador inteligente de 15+ fuentes de deals:
- Epic Games
- Steam
- GOG
- Itch.io
- CheapShark (13 tiendas)
- ITAD (50+ tiendas)
- Fanatical
- GreenManGaming
- Humble Bundle
- GamesPlanet
- Gamesload
- IndieGala
- Bundle Stars
- PlayStation
- Xbox
- Nintendo

Con:
- AI Validation
- Multi-source scoring
- Deduplicación inteligente
- Price history tracking
- Review aggregation

Author: HunDeaBot Team
Version: 3.5.0 - ULTRA MEGA PRO
"""

import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import existing hunters
from modules.epic_hunter import EpicHunter
from modules.steam_hunter import SteamHunter
from modules.gog_hunter import GOGHunter
from modules.itch_hunter import ItchHunter
from modules.cheapshark_hunter import CheapSharkHunter
from modules.itad_hunter import IsThereAnyDealHunter
from modules.gamerpower_hunter import GamerPowerHunter
from modules.ggdeals_hunter import GGDealsHunter

# Import console hunters
from modules.consoles import PlayStationHunter, XboxHunter, NintendoHunter

# Import AI
from modules.ai import SmartDealValidator

# Import utilities
from modules.scoring import SistemaScoring
from modules.reviews_externas import ReviewsExternas
from modules.core.env_config import apply_env_overrides


class MegaAPIAggregator:
    """
    Agregador ultra inteligente de deals de 15+ fuentes.
    """
    
    # API priorities (higher = more trusted)
    SOURCE_TRUST = {
        'steam': 1.0,
        'epic': 1.0,
        'gog': 0.95,
        'playstation': 0.95,
        'xbox': 0.95,
        'nintendo': 0.95,
        'humble': 0.9,
        'fanatical': 0.85,
        'greenmangaming': 0.8,
        'itad': 0.9,
        'cheapshark': 0.85,
        'ggdeals': 0.9,
        'gamerpower': 0.7,
        'itch': 0.7,
        'indiegala': 0.6,
    }
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """
        Initialize mega aggregator.
        
        Args:
            config: Configuration dict
            cache_manager: Cache manager instance
            logger: Logger instance
        """
        self.config = config
        self.cache = cache_manager
        self.logger = logger or logging.getLogger(__name__)
        self.config = apply_env_overrides(self.config, logger=self.logger)
        
        # Initialize AI validator
        itad_key = self.config.get('apis', {}).get('itad')
        self.ai_validator = SmartDealValidator(
            itad_api_key=itad_key,
            logger=logger
        )
        
        # Initialize scoring system
        self.scoring = SistemaScoring(logger=logger)
        
        # Initialize review aggregator
        rawg_key = self.config.get('apis', {}).get('rawg')
        self.reviews = ReviewsExternas(rawg_key, logger=logger) if rawg_key else None
        
        # Stats
        self.stats = {
            'total_sources': 0,
            'successful_sources': 0,
            'failed_sources': 0,
            'total_deals_found': 0,
            'after_dedup': 0,
            'after_ai_filter': 0,
            'fake_deals_blocked': 0,
            'flagged_suspicious': 0
        }

        # Initialize all hunters
        self._init_hunters()
        
        self.logger.info("🚀 MEGA API Aggregator initialized")
        self.logger.info(f"   📊 Sources: {len(self.hunters)}")
        self.logger.info(f"   🧠 AI Validation: {'Enabled' if self.ai_validator else 'Disabled'}")
    
    def _init_hunters(self):
        """Initialize all available hunters."""
        self.hunters = {}
        
        # PC Free Games
        try:
            self.hunters['epic'] = EpicHunter(logger=self.logger)
            self.logger.info("✅ Epic Games hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  Epic hunter failed: {e}")
        
        try:
            self.hunters['steam'] = SteamHunter(logger=self.logger)
            self.logger.info("✅ Steam hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  Steam hunter failed: {e}")
        
        try:
            self.hunters['gog'] = GOGHunter(logger=self.logger)
            self.logger.info("✅ GOG hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  GOG hunter failed: {e}")
        
        try:
            self.hunters['itch'] = ItchHunter(logger=self.logger)
            self.logger.info("✅ Itch.io hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  Itch hunter failed: {e}")
        
        # Multi-store aggregators
        try:
            self.hunters['cheapshark'] = CheapSharkHunter(logger=self.logger)
            self.logger.info("✅ CheapShark (13 stores) loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  CheapShark hunter failed: {e}")
        
        try:
            self.hunters['gamerpower'] = GamerPowerHunter(logger=self.logger)
            self.logger.info("GamerPower hunter loaded")
        except Exception as e:
            self.logger.warning(f"GamerPower hunter failed: {e}")

        try:
            ggdeals_key = self.config.get('apis', {}).get('ggdeals')
            ggdeals_region = self.config.get('apis', {}).get('ggdeals_region')
            if ggdeals_key:
                self.hunters['ggdeals'] = GGDealsHunter(
                    api_key=ggdeals_key,
                    region=ggdeals_region,
                    logger=self.logger
                )
                self.logger.info("GG.deals hunter loaded")
        except Exception as e:
            self.logger.warning(f"GG.deals hunter failed: {e}")

        try:
            itad_key = self.config.get('apis', {}).get('itad')
            if itad_key:
                self.hunters['itad'] = IsThereAnyDealHunter(itad_key, logger=self.logger)
                self.logger.info("✅ ITAD (50+ stores) loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  ITAD hunter failed: {e}")
        
        # Consoles
        try:
            self.hunters['playstation'] = PlayStationHunter(
                self.config, self.cache, self.logger
            )
            self.logger.info("✅ PlayStation hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  PlayStation hunter failed: {e}")
        
        try:
            self.hunters['xbox'] = XboxHunter(
                self.config, self.cache, self.logger
            )
            self.logger.info("✅ Xbox hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  Xbox hunter failed: {e}")
        
        try:
            self.hunters['nintendo'] = NintendoHunter(
                self.config, self.cache, self.logger
            )
            self.logger.info("✅ Nintendo hunter loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  Nintendo hunter failed: {e}")
        
        self.stats['total_sources'] = len(self.hunters)
    
    # ═══════════════════════════════════════════════════════════
    # MULTI-SOURCE FETCHING
    # ═══════════════════════════════════════════════════════════
    
    def fetch_all_deals(self, parallel=True) -> Dict[str, List[Dict]]:
        """
        Fetch deals from ALL sources.
        
        Args:
            parallel: Use parallel fetching (faster)
            
        Returns:
            Dict mapping source -> deals
        """
        self.logger.info("\n" + "="*70)
        self.logger.info("🌐 MEGA HUNT - Fetching from ALL sources")
        self.logger.info("="*70)
        
        all_deals = {}
        
        if parallel:
            all_deals = self._fetch_parallel()
        else:
            all_deals = self._fetch_sequential()
        
        # Calculate stats
        total = sum(len(deals) for deals in all_deals.values())
        self.stats['total_deals_found'] = total
        
        self.logger.info(f"\n📊 Raw Fetch Stats:")
        for source, deals in all_deals.items():
            self.logger.info(f"   {source:15s}: {len(deals)} deals")
        self.logger.info(f"   {'TOTAL':15s}: {total} deals")
        
        return all_deals
    
    def _fetch_parallel(self) -> Dict[str, List[Dict]]:
        """Fetch from all sources in parallel."""
        all_deals = {}
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for source, hunter in self.hunters.items():
                future = executor.submit(self._safe_fetch, source, hunter)
                futures[future] = source
            
            for future in futures:
                source = futures[future]
                try:
                    deals = future.result(timeout=60)
                    all_deals[source] = deals
                    self.stats['successful_sources'] += 1
                except Exception as e:
                    self.logger.error(f"❌ {source} failed: {e}")
                    all_deals[source] = []
                    self.stats['failed_sources'] += 1
        
        return all_deals
    
    def _fetch_sequential(self) -> Dict[str, List[Dict]]:
        """Fetch from all sources sequentially."""
        all_deals = {}
        
        for source, hunter in self.hunters.items():
            deals = self._safe_fetch(source, hunter)
            all_deals[source] = deals
            
            if deals:
                self.stats['successful_sources'] += 1
            else:
                self.stats['failed_sources'] += 1
        
        return all_deals
    
    def _safe_fetch(self, source: str, hunter) -> List[Dict]:
        """Safely fetch from a hunter with error handling."""
        try:
            self.logger.info(f"🔍 Fetching from {source}...")
            
            # Different hunters have different methods
            if hasattr(hunter, 'obtener_juegos_gratis'):
                deals = hunter.obtener_juegos_gratis()
            elif hasattr(hunter, 'hunt'):
                deals = hunter.hunt()
            elif hasattr(hunter, 'fetch_deals'):
                deals = hunter.fetch_deals()
            elif hasattr(hunter, 'get_deals'):
                deals = hunter.get_deals()
            else:
                self.logger.warning(f"⚠️  {source}: Unknown fetch method")
                return []
            
            # Normalize to list
            if not isinstance(deals, list):
                deals = [deals] if deals else []
            
            # CRITICAL: Filter out garbage/unknown deals immediately at source
            valid_deals = []
            junk_keywords = ['dlc', 'pack', 'skin', 'app', 'key', 'giveaway', 'demo', 'bundle', 'addon', 'content']
            
            for deal in deals:
                title = self._get_title(deal)
                title_lower = title.lower() if title else ""
                
                # Check if title is valid and not junk
                is_valid = (
                    title and 
                    title_lower not in ['unknown', 'none', 'null', 'unknown game', ''] and 
                    len(title) > 2 and
                    not any(junk in title_lower for junk in junk_keywords)
                )
                
                if is_valid:
                    if isinstance(deal, dict):
                        deal['source'] = source
                        deal['source_trust'] = self.SOURCE_TRUST.get(source, 0.5)
                    elif hasattr(deal, '__dict__'):
                        deal.source = source
                        deal.source_trust = self.SOURCE_TRUST.get(source, 0.5)
                    valid_deals.append(deal)
                else:
                    self.logger.debug(f"🗑️  Discarded junk/invalid deal from {source}: {title}")
            
            self.logger.info(f"✅ {source}: {len(valid_deals)} valid games found (filtered junk)")
            return valid_deals
            return deals
            
        except Exception as e:
            self.logger.error(f"❌ {source} error: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════
    # INTELLIGENT DEDUPLICATION
    # ═══════════════════════════════════════════════════════════
    
    def deduplicate_deals(self, all_deals: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Intelligent deduplication across sources.
        Keeps best version of each game.
        
        Args:
            all_deals: Dict mapping source -> deals
            
        Returns:
            Deduplicated list
        """
        self.logger.info("\n🔍 Deduplicating deals...")
        
        # Flatten all deals
        flat_deals = []
        for source, deals in all_deals.items():
            flat_deals.extend(deals)
        
        # Group by normalized title
        groups = {}
        
        for deal in flat_deals:
            # Get title
            title = self._get_title(deal)
            normalized = self._normalize_title(title)
            
            if normalized not in groups:
                groups[normalized] = []
            groups[normalized].append(deal)
        
        # Keep best from each group
        deduplicated = []
        
        for normalized, deal_group in groups.items():
            if len(deal_group) == 1:
                deduplicated.append(deal_group[0])
            else:
                best = self._select_best_deal(deal_group)
                deduplicated.append(best)
        
        self.stats['after_dedup'] = len(deduplicated)
        
        self.logger.info(f"✅ Dedup: {len(flat_deals)} → {len(deduplicated)} unique deals")
        
        return deduplicated
    
    def _get_title(self, deal) -> str:
        """Extract title from deal object or dict."""
        if isinstance(deal, dict):
            return deal.get('title') or deal.get('name') or deal.get('titulo') or 'Unknown'
        elif hasattr(deal, 'title'):
            return deal.title
        elif hasattr(deal, 'name'):
            return deal.name
        else:
            return 'Unknown'
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        import re
        
        # Lowercase
        title = title.lower().strip()
        
        # Extract parentheses content
        parentheses = re.findall(r'\(([^)]*)\)', title)
        for content in parentheses:
            title = title.replace(f'({content})', content)
        
        # Remove special chars
        title = re.sub(r'[:-_]', ' ', title)
        
        # Remove common suffixes
        suffixes = [' es gratis', ' is free', ' gratis', ' free', ' demo']
        for suffix in suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)]
        
        # Remove articles
        articles = ['the ', 'a ', 'an ', 'el ', 'la ', 'los ', 'las ']
        for article in articles:
            if title.startswith(article):
                title = title[len(article):]
                break
        
        # Remove multiple spaces
        title = ' '.join(title.split())
        
        return title.strip()
    
    def _select_best_deal(self, deals: List) -> Dict:
        """
        Select best deal from duplicates.
        Priority:
        1. Source trust
        2. Completeness of data
        3. Review score
        """
        scored = []
        
        for deal in deals:
            score = 0.0
            
            # Source trust
            if isinstance(deal, dict):
                score += deal.get('source_trust', 0.5) * 0.4
            elif hasattr(deal, 'source_trust'):
                score += deal.source_trust * 0.4
            
            # Data completeness
            fields = 0
            if self._has_field(deal, 'description'):
                fields += 1
            if self._has_field(deal, 'image_url'):
                fields += 1
            if self._has_field(deal, 'url'):
                fields += 1
            if self._has_field(deal, 'price'):
                fields += 1
            
            score += (fields / 4.0) * 0.3
            
            # Review score
            review_score = self._get_review_score(deal)
            if review_score:
                score += (review_score / 5.0) * 0.3
            
            scored.append((score, deal))
        
        # Return highest scored
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[0][1]
    
    def _has_field(self, deal, field: str) -> bool:
        """Check if deal has field."""
        if isinstance(deal, dict):
            return bool(deal.get(field))
        else:
            return hasattr(deal, field) and bool(getattr(deal, field))
    
    def _get_review_score(self, deal) -> Optional[float]:
        """Get review score from deal."""
        if isinstance(deal, dict):
            return deal.get('review_score') or deal.get('score') or deal.get('rating')
        elif hasattr(deal, 'review_score'):
            return deal.review_score
        elif hasattr(deal, 'score'):
            return deal.score
        elif hasattr(deal, 'rating'):
            return deal.rating
        return None
    
    # ═══════════════════════════════════════════════════════════
    # AI VALIDATION & FILTERING
    # ═══════════════════════════════════════════════════════════
    
    def validate_with_ai(self, deals: List[Dict]) -> List[Dict]:
        """
        Validate deals with AI and flag suspicious ones.
        
        Args:
            deals: List of deals
            
        Returns:
            Deals enriched with AI metadata (no blocking)
        """
        if not self.ai_validator:
            self.logger.warning("AI validator not available - skipping")
            return deals
        
        self.logger.info("\nAI Validation - Flagging suspicious deals...")
        
        # Convert to validation format
        deal_dicts = []
        for deal in deals:
            deal_dict = self._deal_to_dict(deal)
            deal_dicts.append(deal_dict)
        
        # Validate batch
        validated = self.ai_validator.validate_batch(deal_dicts)
        
        # Flag suspicious deals (no blocking)
        processed_deals = []
        suspicious_count = 0
        threshold = self.config.get('filters', {}).get('ai_trust_threshold', 0.6)
        
        for i, validation_result in enumerate(validated):
            original_deal = deals[i]
            trust_score = validation_result.get('trust_score', 0)
            verdict = validation_result.get('validation', {}).get('verdict', '')
            is_suspicious = trust_score < threshold
            
            original_deal = self._enrich_with_ai(original_deal, validation_result, is_suspicious)
            processed_deals.append(original_deal)
            
            if is_suspicious:
                title = self._get_title(original_deal)
                self.logger.warning(
                    f"POSIBLE: {title} "
                    f"(score: {trust_score:.0%}, {verdict})"
                )
                suspicious_count += 1
        
        self.stats['flagged_suspicious'] += suspicious_count
        self.stats['after_ai_filter'] = len(processed_deals)
        
        self.logger.info(
            f"AI Review: {len(deals)} -> {len(processed_deals)} "
            f"({suspicious_count} flagged)"
        )
        
        return processed_deals

    def _deal_to_dict(self, deal) -> Dict:
        """Convert deal to dict for AI validation."""
        if isinstance(deal, dict):
            return {
                'title': self._get_title(deal),
                'current_price': deal.get('current_price', 0) or deal.get('price', 0),
                'original_price': deal.get('original_price', 0) or deal.get('regular_price', 0),
                'discount_percent': deal.get('discount_percent', 0) or deal.get('discount', 0)
            }
        else:
            return {
                'title': self._get_title(deal),
                'current_price': getattr(deal, 'current_price', 0),
                'original_price': getattr(deal, 'original_price', 0),
                'discount_percent': getattr(deal, 'discount_percent', 0)
            }
    
    def _enrich_with_ai(self, deal, validation_result: Dict, is_suspicious: bool):
        """Add AI metadata to deal."""
        trust_score = validation_result.get('trust_score', 0)
        verdict = validation_result.get('validation', {}).get('verdict', '')
        ai_flag = "POSIBLEMENTE" if is_suspicious else "CONFIABLE"
        
        if isinstance(deal, dict):
            deal['ai_verified'] = not is_suspicious
            deal['ai_trust_score'] = trust_score
            deal['ai_verdict'] = verdict
            deal['ai_flag'] = ai_flag
        else:
            deal.ai_verified = not is_suspicious
            deal.ai_trust_score = trust_score
            deal.ai_verdict = verdict
            deal.ai_flag = ai_flag
        
        return deal

    # ═══════════════════════════════════════════════════════════
    # MAIN ORCHESTRATOR
    # ═══════════════════════════════════════════════════════════
    
    def mega_hunt(self, use_ai=True, parallel=True) -> List[Dict]:
        """
        Execute MEGA HUNT across all sources.
        
        Args:
            use_ai: Use AI validation
            parallel: Use parallel fetching
            
        Returns:
            Final curated list of deals
        """
        start_time = datetime.now()
        
        # Step 1: Fetch from all sources
        all_deals = self.fetch_all_deals(parallel=parallel)
        
        # Step 2: Deduplicate
        unique_deals = self.deduplicate_deals(all_deals)
        
        # Step 3: AI validation
        if use_ai:
            verified_deals = self.validate_with_ai(unique_deals)
        else:
            verified_deals = unique_deals
            self.stats['after_ai_filter'] = len(unique_deals)
        
        # Step 4: Enrich with reviews & scoring
        final_deals = self._enrich_deals(verified_deals)
        
        # Final stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info("\n" + "="*70)
        self.logger.info("🎉 MEGA HUNT COMPLETE")
        self.logger.info("="*70)
        self.logger.info(f"Sources queried:    {self.stats['total_sources']}")
        self.logger.info(f"Successful:         {self.stats['successful_sources']}")
        self.logger.info(f"Failed:             {self.stats['failed_sources']}")
        self.logger.info(f"Raw deals:          {self.stats['total_deals_found']}")
        self.logger.info(f"After dedup:        {self.stats['after_dedup']}")
        self.logger.info(f"After AI review:    {self.stats['after_ai_filter']}")
        self.logger.info(f"Suspicious flagged: {self.stats['flagged_suspicious']}")
        self.logger.info(f"Final curated:      {len(final_deals)}")
        self.logger.info(f"Duration:           {duration:.1f}s")
        self.logger.info("="*70)
        
        return final_deals
    
    def _enrich_deals(self, deals: List[Dict]) -> List[Dict]:
        """Enrich deals with additional metadata."""
        deals = self._enrich_with_devices(deals)
        deals = self._enrich_with_ggdeals(deals)
        return deals

    def _enrich_with_ggdeals(self, deals: List[Dict]) -> List[Dict]:
        """Enrich deals using GG.deals Prices API when Steam App IDs are available."""
        gg = self.hunters.get('ggdeals')
        if not gg or not hasattr(gg, 'get_prices_by_steam_app_ids'):
            return deals

        steam_ids = []
        seen = set()

        for deal in deals:
            steam_app_id = self._get_steam_app_id(deal)
            if steam_app_id and steam_app_id not in seen:
                seen.add(steam_app_id)
                steam_ids.append(steam_app_id)

        if not steam_ids:
            return deals

        try:
            region = self.config.get('apis', {}).get('ggdeals_region')
            price_map = gg.get_prices_by_steam_app_ids(steam_ids, region=region)
        except Exception as exc:
            self.logger.warning(f"GG.deals enrichment failed: {exc}")
            return deals

        for deal in deals:
            steam_app_id = self._get_steam_app_id(deal)
            if not steam_app_id:
                continue

            info = price_map.get(str(steam_app_id))
            if not info:
                continue

            prices = info.get('prices', {}) if isinstance(info, dict) else {}

            self._set_deal_field(deal, 'ggdeals_title', info.get('title'))
            self._set_deal_field(deal, 'ggdeals_url', info.get('url'))
            self._set_deal_field(deal, 'ggdeals_currency', prices.get('currency'))
            self._set_deal_field(deal, 'ggdeals_current_retail', self._to_float(prices.get('currentRetail')))
            self._set_deal_field(deal, 'ggdeals_current_keyshops', self._to_float(prices.get('currentKeyshops')))
            self._set_deal_field(deal, 'ggdeals_historical_retail', self._to_float(prices.get('historicalRetail')))
            self._set_deal_field(deal, 'ggdeals_historical_keyshops', self._to_float(prices.get('historicalKeyshops')))
            self._set_deal_field(deal, 'ggdeals_enriched', True)

        return deals

    def _enrich_with_devices(self, deals: List[Dict]) -> List[Dict]:
        # Attach compatible devices to each deal.
        for deal in deals:
            devices = self._infer_devices(deal)
            devices_str = ", ".join(devices) if devices else "Unknown"
            if isinstance(deal, dict):
                deal['devices'] = devices
                deal['devices_str'] = devices_str
            else:
                deal.devices = devices
                deal.devices_str = devices_str
        return deals

    def _infer_devices(self, deal) -> List[str]:
        # Infer compatible devices from deal metadata.
        devices = []

        def add(device: str):
            if device and device not in devices:
                devices.append(device)

        console_gen = self._get_console_gen(deal)
        if console_gen:
            self._add_devices_from_text(console_gen, add)

        platforms = self._get_platforms_list(deal)
        for platform in platforms:
            self._add_devices_from_text(platform, add)

        source = self._get_source_label(deal)
        if source:
            self._add_devices_from_text(source, add)

        title = self._get_title(deal)
        if title:
            self._add_devices_from_text(title, add)

        if not devices and self._is_pc_store(deal):
            add("PC")

        return devices

    def _get_platforms_list(self, deal) -> List[str]:
        # Return platform hints as list of strings.
        platforms = []
        if isinstance(deal, dict):
            value = deal.get('platforms')
            if isinstance(value, list):
                platforms.extend(value)
            elif isinstance(value, str) and value:
                platforms.extend([p.strip() for p in value.split(',') if p.strip()])

            value = deal.get('platform')
            if isinstance(value, str) and value:
                platforms.append(value)

            value = deal.get('console_gen')
            if isinstance(value, str) and value:
                platforms.append(value)

            value = deal.get('tienda')
            if isinstance(value, str) and value:
                platforms.append(value)
        else:
            value = getattr(deal, 'platforms', None)
            if isinstance(value, list):
                platforms.extend(value)
            elif isinstance(value, str) and value:
                platforms.extend([p.strip() for p in value.split(',') if p.strip()])

            value = getattr(deal, 'platform', None)
            if isinstance(value, str) and value:
                platforms.append(value)

            value = getattr(deal, 'console_gen', None)
            if isinstance(value, str) and value:
                platforms.append(value)

        return platforms

    def _get_source_label(self, deal) -> Optional[str]:
        if isinstance(deal, dict):
            return deal.get('source') or deal.get('fuente')
        return getattr(deal, 'source', None)

    def _get_console_gen(self, deal) -> Optional[str]:
        if isinstance(deal, dict):
            return deal.get('console_gen')
        return getattr(deal, 'console_gen', None)

    def _is_pc_store(self, deal) -> bool:
        label = ""
        if isinstance(deal, dict):
            label = (deal.get('platform') or deal.get('tienda') or deal.get('source') or '')
        else:
            label = getattr(deal, 'platform', '') or getattr(deal, 'source', '')
        label = str(label).lower()
        pc_tokens = [
            'steam', 'epic', 'gog', 'itch', 'cheapshark', 'itad', 'ggdeals', 'pc'
        ]
        return any(token in label for token in pc_tokens)

    def _add_devices_from_text(self, text: str, add_fn):
        # Parse a text blob and add device hints.
        if not text:
            return
        t = str(text).lower()

        # Consoles
        if 'ps5' in t or 'playstation 5' in t:
            add_fn('PS5')
        if 'ps4' in t or 'playstation 4' in t:
            add_fn('PS4')
        if 'playstation' in t and 'ps4' not in t and 'ps5' not in t:
            add_fn('PS4')
            add_fn('PS5')

        if 'xbox series' in t or 'xbox series x' in t or 'xbox series s' in t or 'scarlett' in t:
            add_fn('Xbox Series X|S')
        if 'xbox one' in t:
            add_fn('Xbox One')
        if 'xbox' in t and 'series' not in t and 'one' not in t and 'pc' not in t:
            add_fn('Xbox Series X|S')
            add_fn('Xbox One')

        if 'nintendo switch' in t or 'switch' in t:
            add_fn('Nintendo Switch')

        # VR
        if 'steamvr' in t:
            add_fn('PC VR (SteamVR)')
        if 'viveport' in t:
            add_fn('PC VR (Viveport)')
        if 'meta quest' in t or 'oculus quest' in t:
            add_fn('Meta Quest')
        if 'psvr2' in t or 'ps vr2' in t:
            add_fn('PSVR2')
        if 'psvr' in t and 'psvr2' not in t:
            add_fn('PSVR')

        # Mobile
        if 'android' in t:
            add_fn('Android')
        if 'ios' in t or 'iphone' in t or 'ipad' in t:
            add_fn('iOS')

        # PC + OS
        if 'windows' in t:
            add_fn('PC (Windows)')
        if 'macos' in t or 'osx' in t or 'mac' in t:
            add_fn('PC (macOS)')
        if 'linux' in t:
            add_fn('PC (Linux)')
        if 'pc' in t or 'steam' in t or 'epic games' in t or 'gog' in t or 'itch' in t:
            add_fn('PC')

    def _get_steam_app_id(self, deal) -> Optional[str]:
        if isinstance(deal, dict):
            return (
                deal.get('steam_app_id')
                or deal.get('steamAppID')
                or deal.get('steam_appid')
                or deal.get('steam_app')
            )
        if hasattr(deal, 'steam_app_id'):
            return getattr(deal, 'steam_app_id')
        if hasattr(deal, 'steamAppID'):
            return getattr(deal, 'steamAppID')
        return None

    def _set_deal_field(self, deal, field: str, value) -> None:
        if value is None:
            return
        if isinstance(deal, dict):
            deal[field] = value
        else:
            try:
                setattr(deal, field, value)
            except Exception:
                pass

    def _to_float(self, value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    
    def get_stats(self) -> Dict:
        """Get aggregator statistics."""
        return self.stats


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

def test_mega_aggregator():
    """Test mega aggregator."""
    import json
    
    # Load config
    try:
        with open('config.json') as f:
            config = json.load(f)
    except:
        config = {}
    
    # Mock cache
    class MockCache:
        def is_posted(self, game_id):
            return False
        def add_to_cache(self, game_id, data):
            pass
    
    cache = MockCache()
    
    # Initialize
    aggregator = MegaAPIAggregator(config, cache)
    
    # Run mega hunt
    deals = aggregator.mega_hunt(use_ai=False, parallel=True)
    
    print(f"\n🎯 Found {len(deals)} quality deals!")
    
    # Show sample
    for i, deal in enumerate(deals[:5], 1):
        title = aggregator._get_title(deal)
        print(f"{i}. {title}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_mega_aggregator()
