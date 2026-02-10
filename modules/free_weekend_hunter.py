"""
🆓 Free Weekends Hunter - Multi-Platform
─────────────────────────────────────────

Detecta juegos gratis temporales de fin de semana en:
- Steam Free Weekends
- Xbox Free Play Days  
- Epic Games Free (semanal)

Author: HunDeaBot Team
Version: 1.0.0
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re


class FreeWeekendHunter:
    """
    Hunter para juegos gratis temporales de fin de semana.
    """
    
    def __init__(self, logger=None):
        """Initialize hunter."""
        self.logger = logger or logging.getLogger(__name__)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # ═══════════════════════════════════════════════════════════
    # STEAM FREE WEEKENDS
    # ═══════════════════════════════════════════════════════════
    
    def fetch_steam_free_weekends(self) -> List[Dict]:
        """
        Fetch Steam Free Weekend games from SteamDB.
        
        Returns:
            List of free weekend games
        """
        games = []
        
        try:
            self.logger.info("🔍 Fetching Steam Free Weekends from SteamDB...")
            
            url = "https://steamdb.info/upcoming/free/"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find free weekend table
            table = soup.find('table', {'class': 'table'})
            if not table:
                self.logger.warning("⚠️  Steam: No table found")
                return games
            
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                try:
                    cols = row.find_all('td')
                    if len(cols) < 4:
                        continue
                    
                    # Extract game name
                    name_col = cols[1]
                    game_link = name_col.find('a')
                    if not game_link:
                        continue
                    
                    game_name = game_link.text.strip()
                    game_url = f"https://steamdb.info{game_link['href']}"
                    
                    # Extract Steam App ID
                    app_id_match = re.search(r'/app/(\d+)/', game_link['href'])
                    app_id = app_id_match.group(1) if app_id_match else None
                    
                    # Extract dates
                    start_date = cols[2].text.strip()
                    end_date = cols[3].text.strip()
                    
                    # Check if currently active
                    is_active = self._is_date_range_active(start_date, end_date)
                    
                    if is_active or self._is_upcoming(start_date):
                        game = {
                            'name': game_name,
                            'platform': 'Steam',
                            'type': 'Free Weekend',
                            'app_id': app_id,
                            'store_url': f"https://store.steampowered.com/app/{app_id}" if app_id else game_url,
                            'start_date': start_date,
                            'end_date': end_date,
                            'is_active': is_active,
                            'source': 'SteamDB'
                        }
                        
                        games.append(game)
                        self.logger.info(f"✅ Steam: {game_name} ({start_date} - {end_date})")
                
                except Exception as e:
                    self.logger.debug(f"Error parsing Steam row: {e}")
                    continue
            
            self.logger.info(f"📥 Found {len(games)} Steam Free Weekends")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Steam Free Weekends failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ Steam parsing error: {e}")
        
        return games
    
    # ═══════════════════════════════════════════════════════════
    # XBOX FREE PLAY DAYS
    # ═══════════════════════════════════════════════════════════
    
    def fetch_xbox_free_play_days(self) -> List[Dict]:
        """
        Fetch Xbox Free Play Days from Xbox Wire.
        
        Returns:
            List of free play days games
        """
        games = []
        
        try:
            self.logger.info("🔍 Fetching Xbox Free Play Days...")
            
            # Xbox Wire RSS feed or recent posts
            url = "https://news.xbox.com/en-us/"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find "Free Play Days" articles
            articles = soup.find_all('article', limit=20)
            
            for article in articles:
                try:
                    title_elem = article.find('h2') or article.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Check if it's a Free Play Days article
                    if 'free play days' not in title.lower():
                        continue
                    
                    link_elem = title_elem.find('a')
                    article_url = link_elem['href'] if link_elem else None
                    
                    if article_url and not article_url.startswith('http'):
                        article_url = f"https://news.xbox.com{article_url}"
                    
                    # Extract dates from title (e.g., "02-05-2026")
                    date_match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', title)
                    if date_match:
                        month, day, year = date_match.groups()
                        start_date = f"{year}-{month}-{day}"
                        
                        # Usually Thursday to Sunday (3-4 days)
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        end_dt = start_dt + timedelta(days=3)
                        end_date = end_dt.strftime('%Y-%m-%d')
                    else:
                        start_date = "Unknown"
                        end_date = "Unknown"
                    
                    # Try to extract game names from title
                    game_names = self._extract_game_names_from_title(title)
                    
                    if not game_names:
                        # Generic entry
                        game = {
                            'name': title,
                            'platform': 'Xbox',
                            'type': 'Free Play Days',
                            'store_url': article_url or 'https://www.xbox.com',
                            'start_date': start_date,
                            'end_date': end_date,
                            'is_active': self._is_date_range_active(start_date, end_date),
                            'source': 'Xbox Wire'
                        }
                        games.append(game)
                    else:
                        # Individual games
                        for game_name in game_names:
                            game = {
                                'name': game_name,
                                'platform': 'Xbox',
                                'type': 'Free Play Days',
                                'store_url': article_url or 'https://www.xbox.com',
                                'start_date': start_date,
                                'end_date': end_date,
                                'is_active': self._is_date_range_active(start_date, end_date),
                                'source': 'Xbox Wire'
                            }
                            games.append(game)
                            self.logger.info(f"✅ Xbox: {game_name} ({start_date} - {end_date})")
                
                except Exception as e:
                    self.logger.debug(f"Error parsing Xbox article: {e}")
                    continue
            
            self.logger.info(f"📥 Found {len(games)} Xbox Free Play Days")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Xbox Free Play Days failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ Xbox parsing error: {e}")
        
        return games
    
    # ═══════════════════════════════════════════════════════════
    # EPIC GAMES FREE (Integration)
    # ═══════════════════════════════════════════════════════════
    
    def fetch_epic_free_games(self) -> List[Dict]:
        """
        Fetch Epic Games Free weekly games.
        
        Returns:
            List of free Epic games
        """
        games = []
        
        try:
            self.logger.info("🔍 Fetching Epic Games Free...")
            
            # Use Epic Hunter if available
            try:
                from epic_hunter import EpicHunter
                epic_hunter = EpicHunter()
                epic_games = epic_hunter.obtener_juegos_gratis()
                
                for game in epic_games:
                    games.append({
                        'name': game.get('titulo', 'Unknown'),
                        'platform': 'Epic Games',
                        'type': 'Free to Keep',
                        'store_url': game.get('url', 'https://www.epicgames.com/store/'),
                        'start_date': game.get('fecha_inicio', 'Unknown'),
                        'end_date': game.get('fecha_fin', 'Unknown'),
                        'is_active': True,
                        'source': 'Epic Games API',
                        'description': game.get('descripcion', '')
                    })
                    self.logger.info(f"✅ Epic: {game.get('titulo')}")
                
            except ImportError:
                self.logger.warning("⚠️  Epic Hunter not available")
            
            self.logger.info(f"📥 Found {len(games)} Epic free games")
            
        except Exception as e:
            self.logger.error(f"❌ Epic Games fetch failed: {e}")
        
        return games
    
    # ═══════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════
    
    def _is_date_range_active(self, start_str: str, end_str: str) -> bool:
        """Check if date range is currently active."""
        try:
            now = datetime.now()
            
            # Parse start date
            start = self._parse_date(start_str)
            if not start:
                return False
            
            # Parse end date
            end = self._parse_date(end_str)
            if not end:
                # Assume 4 days if no end date
                end = start + timedelta(days=4)
            
            return start <= now <= end
            
        except:
            return False
    
    def _is_upcoming(self, start_str: str, days_ahead: int = 7) -> bool:
        """Check if date is upcoming (within next N days)."""
        try:
            now = datetime.now()
            start = self._parse_date(start_str)
            
            if not start:
                return False
            
            return now <= start <= (now + timedelta(days=days_ahead))
            
        except:
            return False
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        if not date_str or date_str == 'Unknown':
            return None
        
        # Try various formats
        formats = [
            '%Y-%m-%d',
            '%d %B %Y',
            '%B %d, %Y',
            '%m/%d/%Y',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        return None
    
    def _extract_game_names_from_title(self, title: str) -> List[str]:
        """Extract game names from article title."""
        games = []
        
        # Remove common prefixes
        title = re.sub(r'^Free Play Days[:\-–]?', '', title, flags=re.IGNORECASE)
        title = title.strip()
        
        # Split by common delimiters
        if ',' in title or '&' in title or ' and ' in title.lower():
            # Multiple games mentioned
            parts = re.split(r',|&| and ', title, flags=re.IGNORECASE)
            for part in parts:
                game_name = part.strip()
                # Clean up
                game_name = re.sub(r'\d{2}[/-]\d{2}[/-]\d{4}', '', game_name).strip()
                if len(game_name) > 3 and not game_name.lower() in ['takeover', '2026', 'weekend']:
                    games.append(game_name)
        
        return games
    
    # ═══════════════════════════════════════════════════════════
    # GAMERPOWER INTEGRATION (API SOURCE)
    # ═══════════════════════════════════════════════════════════
    
    def fetch_gamerpower_weekends(self) -> List[Dict]:
        """
        Fetch Free Weekends from GamerPower API.
        
        Returns:
            List of free weekend games
        """
        games = []
        try:
            self.logger.info("🔍 Fetching GamerPower Free Weekends...")
            
            # Dynamic import to avoid circular dependency issues if any
            from modules.gamerpower_hunter import GamerPowerHunter
            
            gp_hunter = GamerPowerHunter(logger=self.logger)
            all_free = gp_hunter.hunt_all_free()
            weekends = gp_hunter.filter_free_weekends(all_free)
            
            for item in weekends:
                # Convert to standard format
                game = {
                    'name': item.get('title', 'Unknown'),
                    'platform': ', '.join(item.get('platforms', [])),
                    'type': 'Free Weekend',
                    'store_url': item.get('url', ''),
                    'start_date': item.get('published_date', 'Unknown'),
                    'end_date': item.get('end_date', 'Unknown'),
                    'is_active': True,  # API returns active ones
                    'source': 'GamerPower API',
                    'description': item.get('description', '')
                }
                games.append(game)
                self.logger.info(f"✅ GamerPower: {game['name']}")
                
            self.logger.info(f"📥 Found {len(games)} GamerPower Free Weekends")
            
        except ImportError:
            self.logger.error("❌ GamerPower module not found")
        except Exception as e:
            self.logger.error(f"❌ GamerPower fetch failed: {e}")
            
        return games

    # ═══════════════════════════════════════════════════════════
    # MAIN METHOD
    # ═══════════════════════════════════════════════════════════
    
    def hunt_all_free_weekends(self) -> Dict[str, List[Dict]]:
        """
        Hunt all free weekend games across platforms.
        
        Returns:
            Dict with platform as key and list of games
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("🆓 Starting Free Weekends Hunt")
        self.logger.info("="*60)
        
        # Get data from all sources
        steam_games = self.fetch_steam_free_weekends()
        xbox_games = self.fetch_xbox_free_play_days()
        epic_games = self.fetch_epic_free_games()
        gp_games = self.fetch_gamerpower_weekends()
        
        # Merge GamerPower into platforms if possible, or keep separate
        # For now, let's look for duplicates and merge
        
        results = {
            'steam': steam_games,
            'xbox': xbox_games,
            'epic': epic_games,
            'gamerpower': gp_games
        }
        
        # Count totals
        total_active = sum(
            len([g for g in games if g.get('is_active', False)])
            for games in results.values()
        )
        
        total_upcoming = sum(
            len([g for g in games if not g.get('is_active', False)])
            for games in results.values()
        )
        
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 Free Weekends Hunt Summary")
        self.logger.info("="*60)
        self.logger.info(f"🎮 Steam: {len(results['steam'])} games")
        self.logger.info(f"🟩 Xbox: {len(results['xbox'])} games")
        self.logger.info(f"⭐ Epic: {len(results['epic'])} games")
        self.logger.info(f"🎁 GamerPower: {len(results['gamerpower'])} games")
        self.logger.info(f"✅ Active now: {total_active}")
        self.logger.info(f"🔜 Upcoming: {total_upcoming}")
        self.logger.info("="*60)
        
        return results


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

def test_free_weekend_hunter():
    """Test free weekend hunter."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n🧪 Testing Free Weekend Hunter")
    print("="*60)
    
    hunter = FreeWeekendHunter()
    results = hunter.hunt_all_free_weekends()
    
    # Display results
    print("\n📋 RESULTS:")
    print("="*60)
    
    for platform, games in results.items():
        if games:
            print(f"\n{platform.upper()}:")
            for i, game in enumerate(games, 1):
                status = "🟢 ACTIVE" if game.get('is_active') else "🔜 UPCOMING"
                print(f"\n{i}. {game['name']} {status}")
                print(f"   Platform: {game['platform']}")
                print(f"   Type: {game['type']}")
                print(f"   Dates: {game['start_date']} → {game['end_date']}")
                print(f"   URL: {game['store_url']}")


if __name__ == "__main__":
    test_free_weekend_hunter()
