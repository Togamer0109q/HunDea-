"""
🎮 Base Console Hunter - Professional Architecture
──────────────────────────────────────────────────

Abstract base class for all console hunters.
Provides shared functionality for PlayStation, Xbox, and Nintendo hunters.

Author: HunDeaBot Team
Version: 3.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class ConsoleDeal:
    """Data structure for a console game deal."""
    
    # Core Info
    title: str
    store_url: str
    platform: str  # "PlayStation", "Xbox", "Nintendo"
    console_gen: str  # "PS5", "Xbox Series X", "Switch", etc.
    
    # Pricing
    original_price: float
    current_price: float
    discount_percent: int
    
    # Metadata
    game_id: str  # Unique identifier
    currency: str = "USD"
    release_date: Optional[str] = None
    publisher: Optional[str] = None
    developer: Optional[str] = None
    genre: Optional[str] = None
    
    # Reviews & Scores
    metacritic_score: Optional[int] = None
    user_score: Optional[float] = None
    rawg_score: Optional[float] = None
    total_reviews: Optional[int] = None
    
    # Special Flags
    is_ps_plus: bool = False
    is_game_pass: bool = False
    is_gold_free: bool = False
    is_dlc: bool = False
    is_preorder: bool = False
    
    # Internal
    found_at: datetime = None
    
    def __post_init__(self):
        """Initialize computed fields."""
        if self.found_at is None:
            self.found_at = datetime.now()
    
    @property
    def savings(self) -> float:
        """Calculate total savings in currency."""
        return self.original_price - self.current_price
    
    @property
    def quality_score(self) -> float:
        """Calculate quality score (0.0 - 5.0) using a more flexible weighted average."""
        raw_scores = []
        
        # Metacritic (0-100 normalized to 0-5)
        if self.metacritic_score:
            raw_scores.append(self.metacritic_score / 20.0)
            
        # User Score (0-5)
        if self.user_score:
            raw_scores.append(self.user_score)
            
        # RAWG Score (0-5)
        if self.rawg_score:
            raw_scores.append(self.rawg_score)
            
        if not raw_scores:
            return 0.0
            
        # Average of available scores
        avg_score = sum(raw_scores) / len(raw_scores)
        
        # Bonus for having multiple sources (reliability bonus)
        bonus = 0.2 * (len(raw_scores) - 1)
        
        return min(5.0, avg_score + bonus)
    
    @property
    def is_quality_deal(self) -> bool:
        """Check if this is a quality deal worth posting."""
        return self.quality_score >= 3.5 and self.discount_percent >= 40
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for caching."""
        return {
            'title': self.title,
            'game_id': self.game_id,
            'platform': self.platform,
            'price': self.current_price,
            'discount': self.discount_percent,
            'score': self.quality_score,
            'found_at': self.found_at.isoformat()
        }


class BaseConsoleHunter(ABC):
    """
    Abstract base class for console game hunters.
    
    Each platform (PS, Xbox, Nintendo) should extend this class
    and implement the required abstract methods.
    """
    
    def __init__(self, config: Dict, cache_manager, logger=None):
        """
        Initialize the console hunter.
        
        Args:
            config: Configuration dictionary
            cache_manager: Cache management instance
            logger: Optional logger instance
        """
        self.config = config
        self.cache = cache_manager
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Platform-specific config
        self.platform_name = self.get_platform_name()
        self.platform_config = config.get('filters', {}).get(self.platform_name.lower(), {})
        
        # Filters
        self.min_discount = self.platform_config.get('min_discount', 50)
        self.min_score = self.platform_config.get('min_score', 3.5)
        self.exclude_dlc = self.platform_config.get('exclude_dlc', True)
        self.max_price = self.platform_config.get('max_price', 60)
        
        self.logger.info(f"🎮 {self.platform_name} Hunter initialized")
        self.logger.info(f"📊 Filters: min_discount={self.min_discount}%, min_score={self.min_score}")
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (PlayStation, Xbox, Nintendo)."""
        pass
    
    @abstractmethod
    def fetch_deals(self) -> List[ConsoleDeal]:
        """
        Fetch deals from the platform's API.
        
        Returns:
            List of ConsoleDeal objects
        """
        pass
    
    @abstractmethod
    def get_game_details(self, game_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific game.
        
        Args:
            game_id: Platform-specific game identifier
            
        Returns:
            Dictionary with game details or None
        """
        pass
    
    def filter_deals(self, deals: List[ConsoleDeal]) -> List[ConsoleDeal]:
        """
        Filter deals based on configured criteria.
        
        Args:
            deals: List of all deals
            
        Returns:
            List of filtered quality deals
        """
        filtered = []
        
        for deal in deals:
            # Skip DLC if configured
            if self.exclude_dlc and deal.is_dlc:
                self.logger.debug(f"⏭️  Skipped DLC: {deal.title}")
                continue
            
            # Check discount threshold
            if deal.discount_percent < self.min_discount:
                self.logger.debug(f"⏭️  Low discount ({deal.discount_percent}%): {deal.title}")
                continue
            
            # Check price threshold
            if deal.current_price > self.max_price:
                self.logger.debug(f"⏭️  Too expensive (${deal.current_price}): {deal.title}")
                continue
            
            # Check quality score
            if deal.quality_score < self.min_score:
                self.logger.debug(f"⏭️  Low quality ({deal.quality_score:.1f}): {deal.title}")
                continue
            
            # Check if already posted
            if self.cache.is_posted(deal.game_id):
                self.logger.debug(f"⏭️  Already posted: {deal.title}")
                continue
            
            self.logger.info(f"✅ Quality deal: {deal.title} ({deal.discount_percent}% off, score: {deal.quality_score:.1f})")
            filtered.append(deal)
        
        return filtered
    
    def enrich_deal(self, deal: ConsoleDeal, rawg_api_key: Optional[str] = None) -> ConsoleDeal:
        """
        Enrich deal with external data (RAWG, Metacritic).
        
        Args:
            deal: Base deal object
            rawg_api_key: Optional RAWG API key
            
        Returns:
            Enriched deal object
        """
        if not rawg_api_key:
            return deal
        
        try:
            from ..core.scoring import get_rawg_data
            
            rawg_data = get_rawg_data(deal.title, rawg_api_key)
            if rawg_data:
                deal.rawg_score = rawg_data.get('rating', deal.rawg_score)
                deal.metacritic_score = rawg_data.get('metacritic', deal.metacritic_score)
                deal.genre = rawg_data.get('genres', [{}])[0].get('name', deal.genre)
                
                self.logger.debug(f"📊 Enriched {deal.title}: RAWG={deal.rawg_score}, Meta={deal.metacritic_score}")
        
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to enrich {deal.title}: {e}")
        
        return deal
    
    def hunt(self, rawg_api_key: Optional[str] = None) -> List[ConsoleDeal]:
        """
        Main hunting method - fetch, enrich, and then filter deals.
        
        Args:
            rawg_api_key: Optional RAWG API key for enrichment
            
        Returns:
            List of quality deals ready to post
        """
        self.logger.info(f"🔍 Starting {self.platform_name} hunt...")
        
        # Step 1: Fetch raw deals
        all_deals = self.fetch_deals()
        self.logger.info(f"📥 Fetched {len(all_deals)} total deals")
        
        # Step 2: Enrich ALL deals with external data (RAWG, Metacritic)
        # This is necessary because some sources don't provide scores initially
        self.logger.info(f"📊 Enriching {len(all_deals)} deals...")
        enriched_deals = []
        for deal in all_deals:
            enriched = self.enrich_deal(deal, rawg_api_key)
            
            # Safety: If score is still 0 but discount is huge (>70%), give it a chance
            if enriched.quality_score == 0 and enriched.discount_percent >= 70:
                enriched.rawg_score = 3.0 # Neutral score to pass the filter
                
            enriched_deals.append(enriched)
        
        # Step 3: Filter by quality (now that we have enriched data)
        filtered_deals = self.filter_deals(enriched_deals)
        self.logger.info(f"✨ Filtered to {len(filtered_deals)} quality deals")
        
        self.logger.info(f"✅ {self.platform_name} hunt complete: {len(filtered_deals)} deals ready")
        return filtered_deals
    
    def mark_as_posted(self, deals: List[ConsoleDeal]) -> None:
        """
        Mark deals as posted in cache.
        
        Args:
            deals: List of deals that were posted
        """
        for deal in deals:
            self.cache.add_to_cache(deal.game_id, deal.to_dict())
            self.logger.debug(f"💾 Cached: {deal.title}")
