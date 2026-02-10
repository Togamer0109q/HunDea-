"""
🎮 Console Discord Notifier - Professional Embeds
──────────────────────────────────────────────────

Sends beautifully formatted Discord notifications for console deals.
Separate webhooks for PlayStation, Xbox, and Nintendo.

Author: HunDeaBot Team
Version: 3.0.0
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from modules.consoles.base_console_hunter import ConsoleDeal


class ConsoleNotifier:
    """
    Professional Discord notifier for console game deals.
    """
    
    # Platform colors (Discord embed colors)
    COLORS = {
        'PlayStation': 0x003087,  # PlayStation Blue
        'Xbox': 0x107C10,         # Xbox Green
        'Nintendo': 0xE60012      # Nintendo Red
    }
    
    # Platform emojis
    EMOJIS = {
        'PlayStation': '🟦',
        'Xbox': '🟩',
        'Nintendo': '🟥'
    }
    
    # Quality star ratings
    STAR_RATINGS = {
        (4.5, 5.1): '⭐⭐⭐',
        (3.7, 4.5): '⭐⭐',
        (2.5, 3.7): '⭐',
        (0.0, 2.5): '💭'
    }
    
    def __init__(self, config: Dict, logger=None):
        """
        Initialize console notifier.
        
        Args:
            config: Configuration dictionary with webhooks
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Extract webhooks
        webhooks = config.get('webhooks', {})
        self.webhook_ps = webhooks.get('playstation')
        self.webhook_xbox = webhooks.get('xbox')
        self.webhook_nintendo = webhooks.get('nintendo')
        
        # Extract role IDs
        roles = config.get('roles', {})
        self.role_ps = roles.get('playstation')
        self.role_xbox = roles.get('xbox')
        self.role_nintendo = roles.get('nintendo')
        
        self.logger.info("🎮 Console Notifier initialized")
        self._log_webhook_status()
    
    def _log_webhook_status(self):
        """Log webhook configuration status."""
        webhooks = {
            'PlayStation': self.webhook_ps,
            'Xbox': self.webhook_xbox,
            'Nintendo': self.webhook_nintendo
        }
        
        for platform, webhook in webhooks.items():
            status = "✅ Configured" if webhook else "❌ Missing"
            self.logger.info(f"  {platform}: {status}")
    
    def get_webhook(self, platform: str) -> Optional[str]:
        """Get webhook URL for platform."""
        webhooks = {
            'PlayStation': self.webhook_ps,
            'Xbox': self.webhook_xbox,
            'Nintendo': self.webhook_nintendo
        }
        return webhooks.get(platform)
    
    def get_role_mention(self, platform: str) -> str:
        """Get role mention for platform."""
        roles = {
            'PlayStation': self.role_ps,
            'Xbox': self.role_xbox,
            'Nintendo': self.role_nintendo
        }
        
        role_id = roles.get(platform)
        if role_id:
            return f"<@&{role_id}>"
        return ""
    
    def get_star_rating(self, score: float) -> str:
        """Get star rating string for quality score."""
        for (min_score, max_score), stars in self.STAR_RATINGS.items():
            if min_score <= score < max_score:
                return stars
        return '💭'
    
    def create_deal_embed(self, deal: ConsoleDeal) -> Dict:
        """
        Create professional Discord embed for a console deal.
        
        Args:
            deal: Console deal object
            
        Returns:
            Discord embed dictionary
        """
        # Platform emoji and color
        emoji = self.EMOJIS.get(deal.platform, '🎮')
        color = self.COLORS.get(deal.platform, 0x7289DA)
        
        # Star rating
        stars = self.get_star_rating(deal.quality_score)
        
        # Title
        title = f"{stars} {deal.title}"
        
        # Description
        description_parts = []
        
        # Price info
        if deal.discount_percent > 0:
            description_parts.append(
                f"💰 **${deal.current_price:.2f}** ~~${deal.original_price:.2f}~~ "
                f"**(-{deal.discount_percent}%)**"
            )
        else:
            description_parts.append(f"🆓 **FREE**")
        
        # Quality score
        description_parts.append(f"📊 **Quality Score:** {deal.quality_score:.1f}/5.0")
        
        # Platform
        description_parts.append(f"🎮 **Platform:** {deal.console_gen}")
        devices_str = getattr(deal, 'devices_str', None)
        if not devices_str:
            devices = getattr(deal, 'devices', None)
            if isinstance(devices, list) and devices:
                devices_str = ", ".join(devices)
        if devices_str:
            description_parts.append(f"Compatible: {devices_str}")
        
        # Genre
        if deal.genre:
            description_parts.append(f"🏆 **Genre:** {deal.genre}")
        
        # Special flags
        if deal.is_ps_plus:
            description_parts.append("➕ **PS Plus Exclusive**")
        elif deal.is_game_pass:
            description_parts.append("🎮 **Game Pass Available**")
        
        description = "\n".join(description_parts)
        
        # Fields
        fields = []
        
        # Scores
        scores_value = []
        if deal.metacritic_score:
            scores_value.append(f"🎯 Metacritic: {deal.metacritic_score}/100")
        if deal.user_score:
            scores_value.append(f"⭐ User Score: {deal.user_score:.1f}/5.0")
        
        if scores_value:
            fields.append({
                "name": "📈 Scores",
                "value": "\n".join(scores_value),
                "inline": True
            })
        
        # Publisher/Developer
        info_value = []
        if deal.publisher:
            info_value.append(f"🏢 {deal.publisher}")
        if deal.developer and deal.developer != deal.publisher:
            info_value.append(f"👥 {deal.developer}")
        
        if info_value:
            fields.append({
                "name": "ℹ️ Info",
                "value": "\n".join(info_value),
                "inline": True
            })
        
        # Savings
        if deal.savings > 0:
            fields.append({
                "name": "💸 You Save",
                "value": f"**${deal.savings:.2f}**",
                "inline": True
            })
        
        # Build embed
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": {
                "text": f"{emoji} {deal.platform} Store • HunDeaBot v3.0",
                "icon_url": self._get_platform_icon(deal.platform)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add store button
        if deal.store_url:
            embed["url"] = deal.store_url
        
        return embed
    
    def _get_platform_icon(self, platform: str) -> str:
        """Get platform icon URL."""
        icons = {
            'PlayStation': 'https://i.imgur.com/vFOOwrV.png',
            'Xbox': 'https://i.imgur.com/8bWvFGp.png',
            'Nintendo': 'https://i.imgur.com/cGfqDFU.png'
        }
        return icons.get(platform, '')
    
    def send_deal(self, deal: ConsoleDeal) -> bool:
        """
        Send a single deal notification to Discord.
        
        Args:
            deal: Console deal to send
            
        Returns:
            True if sent successfully
        """
        webhook_url = self.get_webhook(deal.platform)
        
        if not webhook_url or "YOUR_" in webhook_url:
            self.logger.debug(f"⏭️  Skipping notification: Webhook for {deal.platform} not configured")
            return False
        
        try:
            # Create embed
            embed = self.create_deal_embed(deal)
            
            # Role mention
            role_mention = self.get_role_mention(deal.platform)
            
            # Build payload
            payload = {
                "content": role_mention if role_mention else None,
                "embeds": [embed],
                "username": f"{deal.platform} Deals Bot",
                "avatar_url": self._get_platform_icon(deal.platform)
            }
            
            # Send to Discord
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"✅ Sent {deal.platform} deal: {deal.title}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Failed to send {deal.platform} deal: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error sending deal: {e}")
            return False
    
    def send_deals(self, deals: List[ConsoleDeal]) -> Dict[str, int]:
        """
        Send multiple deals to Discord.
        
        Args:
            deals: List of console deals
            
        Returns:
            Dictionary with send statistics
        """
        stats = {
            'total': len(deals),
            'sent': 0,
            'failed': 0,
            'by_platform': {
                'PlayStation': 0,
                'Xbox': 0,
                'Nintendo': 0
            }
        }
        
        for deal in deals:
            if self.send_deal(deal):
                stats['sent'] += 1
                stats['by_platform'][deal.platform] += 1
            else:
                stats['failed'] += 1
        
        # Log summary
        self.logger.info(f"📊 Console Notification Summary:")
        self.logger.info(f"  Total deals: {stats['total']}")
        self.logger.info(f"  Sent: {stats['sent']}")
        self.logger.info(f"  Failed: {stats['failed']}")
        
        for platform, count in stats['by_platform'].items():
            if count > 0:
                emoji = self.EMOJIS.get(platform, '🎮')
                self.logger.info(f"  {emoji} {platform}: {count}")
        
        return stats
    
    def send_status_message(self, platform: str, message: str, is_error: bool = False):
        """
        Send a status message to the platform's webhook.
        
        Args:
            platform: Platform name
            message: Status message
            is_error: Whether this is an error message
        """
        webhook_url = self.get_webhook(platform)
        
        if not webhook_url:
            return
        
        try:
            color = 0xFF0000 if is_error else 0x00FF00
            emoji = "❌" if is_error else "✅"
            
            embed = {
                "title": f"{emoji} {platform} Hunter Status",
                "description": message,
                "color": color,
                "footer": {
                    "text": "HunDeaBot v3.0"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {
                "embeds": [embed],
                "username": f"{platform} Deals Bot"
            }
            
            requests.post(webhook_url, json=payload, timeout=10)
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to send status message: {e}")


# Test function
def test_console_notifier():
    """Test console notifier with sample deals."""
    
    # Sample configuration
    config = {
        'webhooks': {
            'playstation': 'YOUR_PS_WEBHOOK',
            'xbox': 'YOUR_XBOX_WEBHOOK',
            'nintendo': 'YOUR_NINTENDO_WEBHOOK'
        },
        'roles': {
            'playstation': None,
            'xbox': None,
            'nintendo': None
        }
    }
    
    notifier = ConsoleNotifier(config)
    
    # Create sample deals
    sample_deals = [
        ConsoleDeal(
            title="God of War Ragnarök",
            store_url="https://store.playstation.com",
            platform="PlayStation",
            console_gen="PS5",
            original_price=69.99,
            current_price=34.99,
            discount_percent=50,
            currency="USD",
            game_id="ps_test_1",
            genre="Action-Adventure",
            metacritic_score=94,
            user_score=4.8,
            rawg_score=4.7,
            publisher="Sony Interactive Entertainment",
            is_ps_plus=False
        ),
        ConsoleDeal(
            title="Halo Infinite",
            store_url="https://www.xbox.com",
            platform="Xbox",
            console_gen="Xbox Series X|S",
            original_price=59.99,
            current_price=0.00,
            discount_percent=100,
            currency="USD",
            game_id="xbox_test_1",
            genre="FPS",
            metacritic_score=87,
            user_score=4.2,
            publisher="Xbox Game Studios",
            is_game_pass=True
        ),
        ConsoleDeal(
            title="The Legend of Zelda: Tears of the Kingdom",
            store_url="https://www.nintendo.com",
            platform="Nintendo",
            console_gen="Nintendo Switch",
            original_price=69.99,
            current_price=48.99,
            discount_percent=30,
            currency="USD",
            game_id="switch_test_1",
            genre="Action-Adventure",
            metacritic_score=96,
            user_score=4.9,
            publisher="Nintendo"
        )
    ]
    
    print("\n🎮 Console Notifier Test")
    print("="*50)
    print("\nGenerating sample embeds...\n")
    
    for deal in sample_deals:
        embed = notifier.create_deal_embed(deal)
        print(f"{notifier.EMOJIS.get(deal.platform)} {deal.platform} - {deal.title}")
        print(f"  Score: {deal.quality_score:.1f}/5.0")
        print(f"  Embed generated ✅")
        print()


if __name__ == "__main__":
    test_console_notifier()
