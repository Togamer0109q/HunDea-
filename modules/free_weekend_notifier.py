"""
🆓 Free Weekends Notifier - Discord Integration
────────────────────────────────────────────────

Envía notificaciones de juegos gratis de fin de semana a Discord.
Formato especial para urgencia temporal.

Author: HunDeaBot Team
Version: 1.0.0
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime


class FreeWeekendNotifier:
    """
    Discord notifier for free weekend games.
    """
    
    # Platform colors
    COLORS = {
        'Steam': 0x171a21,      # Steam dark
        'Xbox': 0x107C10,       # Xbox green
        'Epic Games': 0x2196F3  # Epic blue
    }
    
    # Urgency colors (override platform colors)
    URGENCY_COLORS = {
        'ending_soon': 0xFF0000,     # Red (< 24h)
        'active': 0x00FF00,          # Green (active now)
        'upcoming': 0xFFA500         # Orange (coming soon)
    }
    
    def __init__(self, webhook_url: str, logger=None):
        """
        Initialize notifier.
        
        Args:
            webhook_url: Discord webhook URL
            logger: Optional logger
        """
        self.webhook_url = webhook_url
        self.logger = logger or logging.getLogger(__name__)
    
    def send_free_weekend_notification(self, game: Dict) -> bool:
        """
        Send notification for a free weekend game.
        
        Args:
            game: Game dictionary
            
        Returns:
            True if successful
        """
        try:
            embed = self._create_embed(game)
            
            payload = {
                'embeds': [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                self.logger.info(f"✅ Sent: {game['name']}")
                return True
            else:
                self.logger.warning(f"⚠️  Failed to send {game['name']}: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error sending notification: {e}")
            return False
    
    def send_batch_notifications(self, games: List[Dict]) -> int:
        """
        Send notifications for multiple games.
        
        Args:
            games: List of game dicts
            
        Returns:
            Number of successful sends
        """
        if not games:
            self.logger.info("📭 No games to send")
            return 0
        
        success_count = 0
        
        for game in games:
            if self.send_free_weekend_notification(game):
                success_count += 1
        
        self.logger.info(f"📤 Sent {success_count}/{len(games)} notifications")
        return success_count
    
    def _create_embed(self, game: Dict) -> Dict:
        """Create Discord embed for a free weekend game."""
        
        # Determine urgency and color
        urgency = self._calculate_urgency(game)
        color = self.URGENCY_COLORS.get(urgency, self.COLORS.get(game['platform'], 0x2f3136))
        
        # Build title with urgency emoji
        urgency_emoji = {
            'ending_soon': '🔥',
            'active': '🟢',
            'upcoming': '🔜'
        }
        
        emoji = urgency_emoji.get(urgency, '🆓')
        title = f"{emoji} {game['name']} - FREE {game['type']}!"
        
        # Build description
        description_parts = []
        
        # Status message
        if urgency == 'ending_soon':
            description_parts.append("⏰ **ENDING SOON!** Grab it before it's gone!")
        elif urgency == 'active':
            description_parts.append("✅ **ACTIVE NOW!** Download and play for free!")
        elif urgency == 'upcoming':
            description_parts.append("🔜 **COMING SOON!** Mark your calendar!")
        
        # Add game description if available
        if game.get('description'):
            description_parts.append(f"\n{game['description']}")
        
        description = "\n".join(description_parts)
        
        # Build fields
        fields = []
        
        # Platform
        fields.append({
            'name': '🎮 Platform',
            'value': game['platform'],
            'inline': True
        })
        
        # Type
        fields.append({
            'name': '📦 Type',
            'value': game['type'],
            'inline': True
        })
        
        # Dates
        date_text = self._format_dates(game)
        fields.append({
            'name': '📅 Availability',
            'value': date_text,
            'inline': False
        })
        
        # Time remaining (if active)
        if game.get('is_active'):
            time_left = self._calculate_time_remaining(game)
            if time_left:
                fields.append({
                    'name': '⏱️ Time Remaining',
                    'value': time_left,
                    'inline': False
                })
        
        # Embed structure
        embed = {
            'title': title,
            'description': description,
            'color': color,
            'fields': fields,
            'url': game.get('store_url', ''),
            'footer': {
                'text': f"Source: {game.get('source', 'Unknown')} | HunDeaBot v3.0"
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add thumbnail if available
        if 'image_url' in game:
            embed['thumbnail'] = {'url': game['image_url']}
        
        return embed
    
    def _calculate_urgency(self, game: Dict) -> str:
        """
        Calculate urgency level.
        
        Returns:
            'ending_soon', 'active', or 'upcoming'
        """
        if not game.get('is_active'):
            return 'upcoming'
        
        # Check if ending soon (< 24h)
        try:
            end_str = game.get('end_date', '')
            if end_str and end_str != 'Unknown':
                # Try to parse end date
                from datetime import datetime, timedelta
                
                # Simple parsing (assumes ISO format)
                try:
                    end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                except:
                    # Try other format
                    try:
                        end_date = datetime.strptime(end_str, '%Y-%m-%d')
                    except:
                        return 'active'
                
                now = datetime.now()
                time_left = end_date - now
                
                if time_left.total_seconds() < 86400:  # 24 hours
                    return 'ending_soon'
        except:
            pass
        
        return 'active'
    
    def _format_dates(self, game: Dict) -> str:
        """Format date range."""
        start = game.get('start_date', 'Unknown')
        end = game.get('end_date', 'Unknown')
        
        if start == 'Unknown' and end == 'Unknown':
            return "Check store for details"
        
        if start != 'Unknown' and end != 'Unknown':
            return f"**{start}** → **{end}**"
        elif start != 'Unknown':
            return f"Starts: **{start}**"
        else:
            return f"Ends: **{end}**"
    
    def _calculate_time_remaining(self, game: Dict) -> Optional[str]:
        """Calculate and format time remaining."""
        try:
            end_str = game.get('end_date', '')
            if not end_str or end_str == 'Unknown':
                return None
            
            from datetime import datetime
            
            try:
                end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            except:
                try:
                    end_date = datetime.strptime(end_str, '%Y-%m-%d')
                    end_date = end_date.replace(hour=23, minute=59)  # Assume end of day
                except:
                    return None
            
            now = datetime.now()
            delta = end_date - now
            
            if delta.total_seconds() < 0:
                return "⚠️ **EXPIRED**"
            
            days = delta.days
            hours = delta.seconds // 3600
            
            if days > 0:
                return f"**{days}** day{'s' if days != 1 else ''}, **{hours}** hour{'s' if hours != 1 else ''}"
            elif hours > 0:
                minutes = (delta.seconds % 3600) // 60
                return f"**{hours}** hour{'s' if hours != 1 else ''}, **{minutes}** min"
            else:
                minutes = delta.seconds // 60
                return f"**{minutes}** minutes ⏰"
            
        except Exception as e:
            return None


# ═══════════════════════════════════════════════════════════
# INTEGRATION EXAMPLE
# ═══════════════════════════════════════════════════════════

def run_free_weekend_hunt_and_notify(webhook_url: str):
    """
    Complete workflow: Hunt and notify.
    
    Args:
        webhook_url: Discord webhook URL
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("\n🆓 Free Weekend Hunt & Notify")
    print("="*60)
    
    # Hunt for free weekends
    from free_weekend_hunter import FreeWeekendHunter
    
    hunter = FreeWeekendHunter(logger=logger)
    results = hunter.hunt_all_free_weekends()
    
    # Prepare notifier
    notifier = FreeWeekendNotifier(webhook_url, logger=logger)
    
    # Send notifications
    total_sent = 0
    
    for platform, games in results.items():
        if games:
            # Filter to only active or ending soon
            active_games = [g for g in games if g.get('is_active', False)]
            
            if active_games:
                logger.info(f"\n📤 Sending {len(active_games)} {platform} notifications...")
                sent = notifier.send_batch_notifications(active_games)
                total_sent += sent
    
    print("\n" + "="*60)
    print(f"✅ Sent {total_sent} total notifications")
    print("="*60)


if __name__ == "__main__":
    # Example usage
    WEBHOOK_URL = "YOUR_WEBHOOK_HERE"
    
    if WEBHOOK_URL != "YOUR_WEBHOOK_HERE":
        run_free_weekend_hunt_and_notify(WEBHOOK_URL)
    else:
        print("⚠️  Set your webhook URL first!")
