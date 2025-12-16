"""
Sistema de notificaciones de Discord para HunDea v2
Maneja los 3 webhooks y formatos de mensajes
"""

import requests
from datetime import datetime

class DiscordNotifier:
    """
    Envía notificaciones a los diferentes canales de Discord
    """
    
    def __init__(self, webhook_premium, webhook_bajos, webhook_weekends, rol_id=None):
        """
        Inicializa el notificador
        
        Args:
            webhook_premium (str): Webhook del canal premium
            webhook_bajos (str): Webhook del canal bajos
            webhook_weekends (str): Webhook del canal free weekends
            rol_id (str): ID del rol a mencionar
        """
        self.webhook_premium = webhook_premium
        self.webhook_bajos = webhook_bajos
        self.webhook_weekends = webhook_weekends
        self.rol_id = rol_id
        
        # Colores por tienda
        self.colores_tienda = {
            'Epic Games': 0x00D9FF,
            'Steam': 0x1B2838,
            'GOG': 0x86328A,
            'Itch.io': 0xFA5C5C
        }
    
    def enviar_juego_premium(self, juego, score, estrellas):
        """
        Envía juego al canal premium
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
        
        Returns:
            bool: True si se envió correctamente
        """
        return self._enviar_notificacion(
            juego, score, estrellas, 
            self.webhook_premium, 
            "premium"
        )
    
    def enviar_juego_bajos(self, juego, score):
        """
        Envía juego al canal bajos
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
        
        Returns:
            bool: True si se envió correctamente
        """
        return self._enviar_notificacion(
            juego, score, "⚠️", 
            self.webhook_bajos, 
            "bajos"
        )
    
    def enviar_free_weekend(self, juego, score, estrellas):
        """
        Envía free weekend al canal correspondiente
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
        
        Returns:
            bool: True si se envió correctamente
        """
        return self._enviar_notificacion(
            juego, score, estrellas, 
            self.webhook_weekends, 
            "weekend"
        )
    
    def _enviar_notificacion(self, juego, score, estrellas, webhook, tipo):
        """
        Envía la notificación a Discord
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
            webhook (str): URL del webhook
            tipo (str): Tipo de canal (premium, bajos, weekend)
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear embed
            embed = self._crear_embed(juego, score, estrellas, tipo)
            
            # Contenido del mensaje
            content = self._crear_contenido_mensaje(tipo)
            
            payload = {
                "content": content,
                "embeds": [embed]
            }
            
            # Enviar
            response = requests.post(webhook, json=payload, timeout=10)
            
            if response.status_code == 204:
                print(f"✅ Enviado a Discord ({tipo}): {juego['titulo']}")
                return True
            else:
                print(f"⚠️ Discord respondió con código {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error al enviar a Discord: {e}")
            return False
    
    def _crear_embed(self, juego, score, estrellas, tipo):
        """
        Crea el embed de Discord
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
            tipo (str): Tipo de canal
        
        Returns:
            dict: Embed de Discord
        """
        tienda = juego.get('tienda', 'Desconocida')
        color = self.colores_tienda.get(tienda, 0x00D9FF)
        
        # Título según tipo
        if tipo == "premium":
            titulo = f"{estrellas} {juego['titulo']}"
        elif tipo == "weekend":
            titulo = f"⏰ {juego['titulo']}"
        else:  # bajos
            titulo = f"⚠️ {juego['titulo']}"
        
        embed = {
            "title": titulo,
            "description": juego['descripcion'][:200] + "..." if len(juego['descripcion']) > 200 else juego['descripcion'],
            "url": juego['url'],
            "color": color,
            "fields": [
                {
                    "name": "🏪 Tienda",
                    "value": tienda,
                    "inline": True
                },
                {
                    "name": "📊 Score HunDea",
                    "value": f"{score:.1f}/5.0",
                    "inline": True
                }
            ],
            "footer": {
                "text": "HunDea v2 • Multi-Store Free Games Hunter"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Agregar reviews si existen
        if 'reviews_percent' in juego and juego['reviews_percent']:
            embed['fields'].append({
                "name": "⭐ Reviews",
                "value": f"{juego['reviews_percent']}% Positivas ({juego['reviews_count']:,} reviews)",
                "inline": False
            })
        
        # Agregar fecha de fin si existe
        if juego.get('fin'):
            timestamp_fin = self._fecha_a_timestamp(juego['fin'])
            if timestamp_fin:
                embed['fields'].append({
                    "name": "⏰ Disponible hasta",
                    "value": timestamp_fin,
                    "inline": False
                })
        
        # Agregar imagen
        if juego.get('imagen'):
            embed["image"] = {"url": juego['imagen']}
        
        return embed
    
    def _crear_contenido_mensaje(self, tipo):
        """
        Crea el contenido del mensaje según el tipo
        
        Args:
            tipo (str): Tipo de canal
        
        Returns:
            str: Contenido del mensaje
        """
        if tipo == "premium":
            content = "🎮 **¡JUEGO GRATIS de CALIDAD!**"
        elif tipo == "weekend":
            content = "⏰ **¡GRATIS ESTE FIN DE SEMANA!**"
        else:  # bajos
            content = "⚠️ **Juego gratis (calidad no verificada)**"
        
        if self.rol_id:
            content += f" <@&{self.rol_id}>"
        
        return content
    
    def _fecha_a_timestamp(self, fecha_str):
        """
        Convierte fecha ISO a Discord timestamp
        
        Args:
            fecha_str (str): Fecha en formato ISO
        
        Returns:
            str: Timestamp de Discord
        """
        try:
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            timestamp = int(fecha.timestamp())
            return f"<t:{timestamp}:F>"
        except:
            return None
