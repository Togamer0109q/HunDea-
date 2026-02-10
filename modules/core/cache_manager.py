"""
💾 Cache Manager - HunDeaBot
─────────────────────────────

Simple cache manager for game deduplication.
"""

import json
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime, timedelta


class CacheManager:
    """Simple cache manager for deduplication."""

    def __init__(self, cache_file: str = 'cache.json'):
        self.cache_file = Path(cache_file)
        self.logger = logging.getLogger(__name__)
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Migrar formato antiguo (lista) a nuevo (dict)
                    if isinstance(data, dict) and 'juegos_anunciados' in data:
                        self.logger.info("🔄 Migrating old cache format...")
                        old_list = data.get('juegos_anunciados', [])
                        new_cache = {}

                        for game_id in old_list:
                            new_cache[game_id] = {
                                'game_id': game_id,
                                'posted_at': '2000-01-01T00:00:00'
                            }

                        self.cache = new_cache
                        self._save_cache()
                        self.logger.info(f"✅ Migrated {len(new_cache)} cached entries")
                        return new_cache

                    return data if isinstance(data, dict) else {}

            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load cache: {e}")

        return {}

    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Failed to save cache: {e}")

    def is_posted(self, game_id: str) -> bool:
        """Check if game was already posted."""
        return game_id in self.cache

    def add_to_cache(self, game_id: str, data: Dict):
        """Add game to cache."""
        self.cache[game_id] = {
            **data,
            'posted_at': datetime.now().isoformat()
        }
        self._save_cache()

    def cleanup_old_entries(self, days: int = 30):
        """Remove cache entries older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)

        old_count = len(self.cache)
        new_cache = {}

        for k, v in self.cache.items():
            if not isinstance(v, dict):
                continue

            try:
                posted_date = datetime.fromisoformat(
                    v.get('posted_at', '2000-01-01')
                )
                if posted_date > cutoff:
                    new_cache[k] = v
            except (ValueError, TypeError):
                new_cache[k] = v

        self.cache = new_cache
        removed = old_count - len(self.cache)

        if removed > 0:
            self.logger.info(f"🧹 Cleaned {removed} old cache entries")
            self._save_cache()
