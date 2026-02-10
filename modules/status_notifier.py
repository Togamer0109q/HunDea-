"""
📊 Status Notifier - HunDeaBot
─────────────────────────────

Generates and sends a "Dashboard" status message to Discord
with cache statistics and GitHub Actions run information.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import requests

class StatusNotifier:
    """Sends bot status and statistics to Discord."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.webhook_url = config.get('notifiers', {}).get('discord', {}).get('webhook_url')
        self.cache_file = Path('cache.json')
        
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Calculates statistics from the cache file."""
        if not self.cache_file.exists():
            return {"total": 0, "platforms": {}}
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                
            total = len(cache)
            platforms = {}
            
            for item in cache.values():
                if isinstance(item, dict):
                    p = item.get('platform', 'Unknown')
                    platforms[p] = platforms.get(p, 0) + 1
                    
            return {
                "total": total,
                "platforms": platforms,
                "size_kb": round(self.cache_file.stat().st_size / 1024, 2)
            }
        except Exception as e:
            self.logger.error(f"❌ Error reading cache for stats: {e}")
            return {"total": 0, "platforms": {}}

    def send_dashboard(self, deals_found: int, deals_posted: int):
        """Sends a dashboard-style embed to Discord."""
        if not self.webhook_url or "YOUR_" in self.webhook_url:
            self.logger.warning("⚠️ Dashboard NOT sent: Webhook URL is missing or using placeholder in config.json")
            return

        stats = self._get_cache_stats()
        
        # GitHub Actions context
        run_id = os.getenv('GITHUB_RUN_ID')
        repository = os.getenv('GITHUB_REPOSITORY')
        workflow = os.getenv('GITHUB_WORKFLOW', 'Manual Run')
        
        github_url = f"https://github.com/{repository}/actions/runs/{run_id}" if run_id else None
        
        # Build platforms string
        platforms_str = "\n".join([f"• **{p}**: {count} juegos" for p, count in stats['platforms'].items()])
        
        embed = {
            "title": "📊 HunDeaBot v3.0 - Dashboard de Estado",
            "color": 0x3498db,  # Blue
            "description": f"Resumen de la ejecución actual y estado del sistema.",
            "fields": [
                {
                    "name": "🚀 Ejecución Actual",
                    "value": (
                        f"• **Deals encontrados**: {deals_found}\n"
                        f"• **Deals publicados**: {deals_posted}\n"
                        f"• **Workflow**: {workflow}"
                    ),
                    "inline": True
                },
                {
                    "name": "💾 Estado de la Caché",
                    "value": (
                        f"• **Total en caché**: {stats['total']}\n"
                        f"• **Tamaño**: {stats['size_kb']} KB\n"
                        f"{platforms_str}"
                    ),
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        if github_url:
            embed["fields"].append({
                "name": "🔗 GitHub Actions",
                "value": f"[Ver ejecución en GitHub]({github_url})",
                "inline": False
            })
            
        payload = {
            "username": "HunDeaBot Status",
            "avatar_url": "https://i.imgur.com/vHqB0yv.png",
            "embeds": [embed]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info("✅ Dashboard status sent to Discord")
        except Exception as e:
            self.logger.error(f"❌ Failed to send dashboard: {e}")

    def send_error_report(self, error_msg: str):
        """Sends a simplified error report if something fails."""
        if not self.webhook_url: return
        
        payload = {
            "embeds": [{
                "title": "❌ HunDeaBot - Error en la ejecución",
                "color": 0xe74c3c, # Red
                "description": f"Se ha producido un error durante el hunting:\n```\n{error_msg[:1000]}\n```",
                "timestamp": datetime.now().isoformat()
            }]
        }
        requests.post(self.webhook_url, json=payload)