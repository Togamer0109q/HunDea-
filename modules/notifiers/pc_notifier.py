"""
💻 PC Discord Notifier - LEGACY STYLE (v2 logic in v3)
──────────────────────────────────────────────────────
Routes deals to specific channels with exact v2 formatting.
"""

import requests
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime

class PCNotifier:
    def __init__(self, config: Dict, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        webhooks = config.get('webhooks', {})
        self.webhook_premium = webhooks.get('pc_premium')
        self.webhook_deals = webhooks.get('pc_deals')
        self.webhook_weekends = webhooks.get('pc_weekends')
        self.webhook_bajos = webhooks.get('pc_bajos')
        self.webhook_todos = webhooks.get('pc_all')

        roles = config.get('roles', {})
        self.role_premium = roles.get('pc_premium')
        self.role_deals = roles.get('pc_deals')
        self.role_weekends = roles.get('pc_weekends')
        self.role_bajos = roles.get('pc_bajos')

        # Threshold requested by user: < 3.4 is low quality
        self.premium_threshold = config.get('features', {}).get('premium_threshold', 3.4)
        
        self.colores_tienda = {
            'Epic Games': 0x00D9FF,
            'Steam': 0x1B2838,
            'GOG': 0x86328A,
            'Itch.io': 0xFA5C5C,
            'PC': 0xFFFFFF
        }

    def _get_game_title(self, deal: Dict) -> str:
        """Robust title extraction from any possible field."""
        title = (deal.get('titulo') or 
                 deal.get('title') or 
                 deal.get('name') or 
                 'Unknown Game')
        return str(title).strip()

    def create_v2_embed(self, deal: Dict, score: float, tipo: str) -> Dict:
        """Creates an embed exactly like HunDea v2."""
        tienda = deal.get('tienda') or deal.get('store') or deal.get('source') or 'PC Store'
        color = self.colores_tienda.get(tienda, 0x00D9FF)
        titulo_juego = self._get_game_title(deal)
        url = deal.get('url') or deal.get('store_url', '')
        
        # Stars logic
        num_stars = int(score) if score > 0 else 0
        estrellas = "⭐" * num_stars if num_stars > 0 else "⚠️"
        
        if tipo == "todos":
            titulo_embed = f"{titulo_juego} es GRATIS"
        elif tipo == "premium":
            titulo_embed = f"{estrellas} {titulo_juego}"
        elif tipo == "weekend":
            titulo_embed = f"⏰ {titulo_juego}"
        elif tipo == "deals":
            titulo_embed = f"💸 {titulo_juego}"
        else: # bajos
            titulo_embed = f"⚠️ {titulo_juego}"
            
        embed = {
            "title": titulo_embed,
            "url": url,
            "color": color,
            "fields": [
                {
                    "name": "🏪 Tienda",
                    "value": tienda,
                    "inline": True
                }
            ],
            "footer": {
                "text": "HunDea v2.7 • Multi-Store Free Games Hunter"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Prices
        precio_actual = deal.get('precio_actual', 0)
        precio_regular = deal.get('precio_regular', 0)
        
        if tipo == "deals":
            descuento = deal.get('descuento_porcentaje', 0)
            embed["fields"].append({
                "name": "💰 Precio",
                "value": f"${precio_regular:.2f} → **${precio_actual:.2f}**",
                "inline": True
            })
            embed["fields"].append({
                "name": "📊 Descuento",
                "value": f"**-{descuento}%**",
                "inline": True
            })
        else:
            embed["fields"].append({
                "name": "💰 Precio",
                "value": "**FREE** (100% OFF)",
                "inline": True
            })

        # Score
        if tipo != "todos":
            embed['fields'].append({
                "name": "📊 Score HunDea",
                "value": f"{score:.1f}/5.0",
                "inline": True
            })

        # Reviews
        rev_per = deal.get('reviews_percent') or deal.get('reviews_score')
        rev_count = deal.get('reviews_count')
        if rev_per:
            embed['fields'].append({
                "name": "⭐ Reviews",
                "value": f"{rev_per}% Positivas ({rev_count or '?' :,} reviews)",
                "inline": False
            })

        # Image
        image = deal.get('imagen') or deal.get('image_url') or deal.get('image')
        if image:
            embed["image"] = {"url": image}
            
        return embed

    def send_deal(self, deal: Dict) -> bool:
        """Sends deal to multiple channels based on v2 logic. Returns True if title is valid."""
        title = self._get_game_title(deal)
        
        # CRITICAL: DO NOT SEND IF TITLE IS UNKNOWN OR EMPTY
        if not title or title.lower() in ['unknown game', 'none', 'unknown', 'null']:
            self.logger.warning(f"🚫 BLOCKED: Deal without valid title from {deal.get('source', 'unknown')}")
            return False

        score = deal.get('quality_score') or deal.get('score', 0)
        precio = deal.get('precio_actual', 0)
        is_free = (precio == 0) or deal.get('is_free', False)
        
        destinations = [] # List of (webhook, type, role)
        
        # 1. Logic for "ALL" channel (Always send if free)
        if self.webhook_todos and is_free:
            destinations.append((self.webhook_todos, "todos", None))
            
        # 2. Logic for specific channels
        if not is_free:
            # Paid deal
            if self.webhook_deals:
                destinations.append((self.webhook_deals, "deals", self.role_deals))
        elif 'weekend' in str(deal.get('type', '')).lower():
            # Free weekend
            if self.webhook_weekends:
                destinations.append((self.webhook_weekends, "weekend", self.role_weekends))
        elif score >= self.premium_threshold:
            # Quality Free Game (Premium)
            if self.webhook_premium:
                destinations.append((self.webhook_premium, "premium", self.role_premium))
        else:
            # Low quality/unverified (Gamelowers)
            webhook = self.webhook_bajos or self.webhook_deals
            role = self.role_bajos or self.role_deals
            if webhook:
                destinations.append((webhook, "bajos", role))

        # Send to all determined destinations
        success = False
        for webhook, tipo, role_id in destinations:
            if not webhook or "YOUR_" in webhook or not webhook.startswith('http'):
                continue
            
            try:
                # ANTI RATE LIMIT: Sleep a bit before each request
                time.sleep(1.5)
                
                embed = self.create_v2_embed(deal, score, tipo)
                
                # Content Message (exactly like v2)
                if tipo == "todos":
                    tienda = deal.get('tienda') or deal.get('store') or deal.get('source') or 'tienda'
                    content = f"🎮 **¡Nuevo juego GRATIS en {tienda}!**"
                elif tipo == "premium":
                    content = "🎮 **¡JUEGO GRATIS de CALIDAD!**"
                elif tipo == "weekend":
                    content = "⏰ **¡GRATIS ESTE FIN DE SEMANA!**"
                elif tipo == "deals":
                    descuento = deal.get('descuento_porcentaje', 0)
                    content = f"💰 **¡GRAN DESCUENTO (-{descuento}%)!**"
                else: # bajos
                    content = "⚠️ **Juego gratis (calidad no verificada)**"
                
                if role_id:
                    content += f" <@&{role_id}>"

                payload = {"content": content, "embeds": [embed]}
                resp = requests.post(webhook, json=payload, timeout=10)
                
                if resp.status_code == 204:
                    success = True
                elif resp.status_code == 429:
                    self.logger.error("🛑 DISCORD RATE LIMIT! Sleeping 5 seconds...")
                    time.sleep(5)
                    # Retry once
                    requests.post(webhook, json=payload, timeout=10)
            except Exception as e:
                self.logger.error(f"Error sending to {tipo}: {e}")
                
        return success

    def send_deals(self, deals: List[Dict]):
        """Handles sending multiple deals with safety."""
        for deal in deals:
            self.send_deal(deal)
