"""
💻 PC Discord Notifier - Professional Embeds
────────────────────────────────────────────

Sends beautifully formatted Discord notifications for PC deals.
Handles Epic Games, Steam, and other PC platforms.

Author: HunDeaBot Team
Version: 3.0.0
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

class PCNotifier:
    """
    Professional Discord notifier for PC game deals.
    """
    
    # Platform colors (Discord embed colors)
    COLORS = {
        'Epic Games': 0x000000,   # Epic Black/White (using black here)
        'Steam': 0x1b2838,        # Steam Blue
        'GOG': 0x800080,          # GOG Purple
        'PC': 0xFFFFFF            # Generic White
    }
    
    # Platform emojis
    EMOJIS = {
        'Epic Games': '⭐',
        'Steam': '💨',
        'GOG': '🟪',
        'PC': '💻'
    }
    
    def __init__(self, config: Dict, logger=None):
        """
        Initialize PC notifier.
        
        Args:
            config: Configuration dictionary with webhooks
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Extract webhooks
        webhooks = config.get('webhooks', {})
        self.webhook_deals = webhooks.get('pc_deals')
        self.webhook_premium = webhooks.get('pc_premium')
        self.webhook_weekends = webhooks.get('pc_weekends')
        
        # Extract role IDs
        roles = config.get('roles', {})
        self.role_deals = roles.get('pc_deals')
        self.role_premium = roles.get('pc_premium')
        
        self.logger.info("💻 PC Notifier initialized")
    
    def get_webhook(self, category: str = 'deals') -> Optional[str]:
        """Get webhook URL for category."""
        if category == 'premium':
            return self.webhook_premium
        elif category == 'weekends':
            return self.webhook_weekends
        return self.webhook_deals
    
    def get_role_mention(self, category: str = 'deals') -> str:
        """Get role mention for category."""
        role_id = self.role_premium if category == 'premium' else self.role_deals
        if role_id:
            return f"<@&{role_id}>"
        return ""
    
    def create_deal_embed(self, deal: Dict) -> Dict:
        """
        Create professional Discord embed for a PC deal.
        
        Args:
            deal: Dictionary containing deal info (Epic format for now)
            
        Returns:
            Discord embed dictionary
        """
        platform = deal.get('tienda', 'PC')
        emoji = self.EMOJIS.get(platform, '💻')
        color = self.COLORS.get(platform, 0xFFFFFF)
        
        # Title
        title = f"{emoji} {deal.get('titulo', 'Unknown Game')}"
        if platform == 'Epic Games':
             title += " - FREE GAME"
        
        # Description
        description = deal.get('descripcion', '')
        if len(description) > 200:
            description = description[:197] + "..."
            
        # Build embed
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": [],
            "footer": {
                "text": f"{platform} Store • HunDeaBot v3.0",
                "icon_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Epic_Games_logo.svg" if platform == 'Epic Games' else ""
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add fields
        if deal.get('fin'):
            # Format date if possible, otherwise use raw
            try:
                date_obj = datetime.fromisoformat(deal['fin'].replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y-%m-%d %H:%M UTC')
                embed['fields'].append({
                    "name": "⏰ Ends",
                    "value": date_str,
                    "inline": True
                })
            except:
                pass
                
        # Price (Free)
        embed['fields'].append({
            "name": "💰 Price",
            "value": "**FREE** (100% OFF)",
            "inline": True
        })

        # Image
        if deal.get('imagen'):
            embed['image'] = {'url': deal['imagen']}
            
        # URL
        if deal.get('url'):
            embed['url'] = deal['url']
            
        return embed
    
    def send_deal(self, deal: Dict) -> bool:
        """
        Send a single deal notification to Discord.
        
        Args:
            deal: Deal dictionary
            
        Returns:
            True if sent successfully
        """
        # For free games, use premium or deals webhook
        webhook_url = self.get_webhook('deals')
        
        if not webhook_url or "YOUR_" in webhook_url:
            self.logger.debug(f"⏭️  Skipping PC notification: Webhook not configured")
            return False
        
        try:
            embed = self.create_deal_embed(deal)
            role_mention = self.get_role_mention('deals')
            
            payload = {
                "content": role_mention if role_mention else None,
                "embeds": [embed],
                "username": "PC Deals Hunter",
                "avatar_url": "https://i.imgur.com/4c76gK5.png" # Generic PC icon
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"✅ Sent PC deal: {deal.get('titulo')}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Failed to send PC deal: {e}")
            return False

    def send_deals(self, deals: List[Dict]) -> Dict[str, int]:
        """
        Send multiple deals.
        """
        stats = {'total': len(deals), 'sent': 0, 'failed': 0}
        
        for deal in deals:
            if self.send_deal(deal):
                stats['sent'] += 1
            else:
                stats['failed'] += 1
                
        self.logger.info(f"📊 PC Notification Summary: {stats['sent']}/{stats['total']} sent")
        return stats
