"""
Sistema de notificaciones de status para GitHub Actions
Envía alertas sobre el estado del workflow
"""

import requests
from datetime import datetime

class StatusNotifier:
    """
    Envía notificaciones de status del workflow a Discord
    """
    
    def __init__(self, webhook_url):
        """
        Inicializa el notificador de status
        
        Args:
            webhook_url (str): Webhook de Discord para status
        """
        self.webhook_url = webhook_url
    
    def notificar_inicio(self):
        """
        Notifica que el workflow ha iniciado
        
        Returns:
            bool: True si se envió correctamente
        """
        embed = {
            "title": "🚀 HunDea v2 - Workflow Iniciado",
            "description": "Buscando juegos gratis en todas las tiendas...",
            "color": 0x3498db,  # Azul
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "HunDea v2 Status"
            }
        }
        
        return self._enviar(embed)
    
    def notificar_exito(self, juegos_premium, juegos_bajos, juegos_total):
        """
        Notifica que el workflow terminó exitosamente
        
        Args:
            juegos_premium (int): Juegos enviados a premium
            juegos_bajos (int): Juegos enviados a bajos
            juegos_total (int): Total de juegos encontrados
        
        Returns:
            bool: True si se envió correctamente
        """
        embed = {
            "title": "✅ HunDea v2 - Completado Exitosamente",
            "description": f"Búsqueda de juegos gratis finalizada",
            "color": 0x2ecc71,  # Verde
            "fields": [
                {
                    "name": "📊 Juegos encontrados",
                    "value": f"{juegos_total} juego(s)",
                    "inline": True
                },
                {
                    "name": "⭐ Premium",
                    "value": f"{juegos_premium} enviado(s)",
                    "inline": True
                },
                {
                    "name": "⚠️ Bajos",
                    "value": f"{juegos_bajos} enviado(s)",
                    "inline": True
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "HunDea v2 Status"
            }
        }
        
        return self._enviar(embed)
    
    def notificar_error(self, mensaje_error):
        """
        Notifica que el workflow falló
        
        Args:
            mensaje_error (str): Descripción del error
        
        Returns:
            bool: True si se envió correctamente
        """
        embed = {
            "title": "❌ HunDea v2 - Error en Workflow",
            "description": f"El workflow encontró un error",
            "color": 0xe74c3c,  # Rojo
            "fields": [
                {
                    "name": "🐛 Error",
                    "value": mensaje_error[:1000],  # Limitar a 1000 chars
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "HunDea v2 Status"
            }
        }
        
        return self._enviar(embed)
    
    def _enviar(self, embed):
        """
        Envía el embed a Discord
        
        Args:
            embed (dict): Embed a enviar
        
        Returns:
            bool: True si se envió correctamente
        """
        if not self.webhook_url or self.webhook_url == "TU_WEBHOOK_AQUI":
            return False
        
        try:
            payload = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 204
        except Exception as e:
            print(f"⚠️ Error al enviar status: {e}")
            return False
