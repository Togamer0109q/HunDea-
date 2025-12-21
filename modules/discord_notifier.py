"""
Sistema de notificaciones de Discord para HunDea v2
Maneja los 5 webhooks y formatos de mensajes
"""

import requests
from datetime import datetime

class DiscordNotifier:
    """
    Envía notificaciones a los diferentes canales de Discord
    """
    
    def __init__(
        self,
        webhook_premium,
        webhook_bajos,
        webhook_weekends,
        webhook_deals=None,
        webhook_todos=None,
        rol_premium=None,
        rol_bajos=None,
        rol_weekends=None,
        rol_deals=None,
        rol_todos=None
    ):
        """
        Inicializa el notificador
        
        Args:
            webhook_premium (str): Webhook del canal premium
            webhook_bajos (str): Webhook del canal bajos
            webhook_weekends (str): Webhook del canal free weekends
            webhook_deals (str, optional): Webhook del canal deals/descuentos
            webhook_todos (str, optional): Webhook del canal todos los juegos
            rol_premium (str, optional): ID del rol premium
            rol_bajos (str, optional): ID del rol bajos
            rol_weekends (str, optional): ID del rol weekends
            rol_deals (str, optional): ID del rol deals
            rol_todos (str, optional): ID del rol todos
        """
        self.webhook_premium = webhook_premium
        self.webhook_bajos = webhook_bajos
        self.webhook_weekends = webhook_weekends
        self.webhook_deals = webhook_deals
        self.webhook_todos = webhook_todos

        self.rol_premium = rol_premium
        self.rol_bajos = rol_bajos
        self.rol_weekends = rol_weekends
        self.rol_deals = rol_deals
        self.rol_todos = rol_todos
        
        # Colores por tienda
        self.colores_tienda = {
            'Epic Games': 0x00D9FF,
            'Steam': 0x1B2838,
            'GOG': 0x86328A,
            'Itch.io': 0xFA5C5C
        }
    
    def enviar_juego_premium(self, juego, score, estrellas):
        """
        Envía juego al canal premium Y al canal todos
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
        
        Returns:
            bool: True si se envió correctamente (canal premium)
        """
        enviado = self._enviar_notificacion(
            juego, score, estrellas, 
            self.webhook_premium, 
            "premium",
            self.rol_premium
        )

        # También enviar a "todos" si está configurado
        if self.webhook_todos:
            self._enviar_notificacion(
                juego, score, estrellas, 
                self.webhook_todos, 
                "todos",
                self.rol_todos
            )
        
        return enviado
    
    def enviar_juego_bajos(self, juego, score):
        """
        Envía juego al canal bajos Y al canal todos
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
        
        Returns:
            bool: True si se envió correctamente (canal bajos)
        """
        estrellas = "⚠️"
        enviado = self._enviar_notificacion(
            juego, score, estrellas, 
            self.webhook_bajos, 
            "bajos",
            self.rol_bajos
        )

        # También enviar a "todos" si está configurado
        if self.webhook_todos:
            self._enviar_notificacion(
                juego, score, estrellas, 
                self.webhook_todos, 
                "todos",
                self.rol_todos
            )
        
        return enviado
    
    def enviar_free_weekend(self, juego, score, estrellas):
        """
        Envía free weekend al canal correspondiente Y al canal todos
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
        
        Returns:
            bool: True si se envió correctamente (canal weekend)
        """
        enviado = self._enviar_notificacion(
            juego, score, estrellas, 
            self.webhook_weekends, 
            "weekend",
            self.rol_weekends
        )

        # También enviar a "todos" si está configurado
        if self.webhook_todos:
            self._enviar_notificacion(
                juego, score, estrellas, 
                self.webhook_todos, 
                "todos",
                self.rol_todos
            )
        
        return enviado
    
    def _enviar_notificacion(self, juego, score, estrellas, webhook, tipo, rol_id):
        """
        Envía la notificación a Discord
        
        Args:
            juego (dict): Info del juego
            score (float): Score del juego
            estrellas (str): Estrellas emoji
            webhook (str): URL del webhook
            tipo (str): Tipo de canal (premium, bajos, weekend, todos)
            rol_id (str): ID del rol a mencionar
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear embed
            embed = self._crear_embed(juego, score, estrellas, tipo)
            
            # Contenido del mensaje (pasar tienda para "todos")
            tienda = juego.get('tienda', 'Desconocida')
            content = self._crear_contenido_mensaje(tipo, tienda, rol_id)
            
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
        if tipo == "todos":
            titulo = f"{juego['titulo']} es GRATIS"
        elif tipo == "premium":
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
                }
            ],
            "footer": {
                "text": "HunDea v2 • Multi-Store Free Games Hunter"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Agregar score solo si NO es el canal "todos"
        if tipo != "todos":
            embed['fields'].append({
                "name": "📊 Score HunDea",
                "value": f"{score:.1f}/5.0",
                "inline": True
            })
        
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
    
    def _crear_contenido_mensaje(self, tipo, tienda=None, rol_id=None):
        """
        Crea el contenido del mensaje según el tipo
        
        Args:
            tipo (str): Tipo de canal
            tienda (str, optional): Nombre de la tienda (usada en "todos")
            rol_id (str, optional): ID del rol a mencionar
        
        Returns:
            str: Contenido del mensaje
        """
        if tipo == "todos":
            tienda_str = tienda or "la tienda"
            content = f"🎮 **¡Nuevo juego GRATIS en {tienda_str}!**"
        elif tipo == "premium":
            content = "🎮 **¡JUEGO GRATIS de CALIDAD!**"
        elif tipo == "weekend":
            content = "⏰ **¡GRATIS ESTE FIN DE SEMANA!**"
        else:  # bajos
            content = "⚠️ **Juego gratis (calidad no verificada)**"
        
        # Agregar mención de rol si existe
        if rol_id:
            content += f" <@&{rol_id}>"
        
        return content
    
    def enviar_oferta_descuento(self, juego, score, estrellas):
        """
        Envía una oferta con descuento al canal de deals
        
        Args:
            juego (dict): Información del juego
            score (float): Score calculado
            estrellas (str): Representación en estrellas
        
        Returns:
            bool: True si se envió correctamente
        """
        if not self.webhook_deals:
            print("⚠️  Webhook de deals no configurado")
            return False
        
        try:
            # Formatear precio
            precio_actual = juego.get('precio_actual', 0)
            precio_regular = juego.get('precio_regular', 0)
            descuento = juego.get('descuento_porcentaje', 0)
            moneda = juego.get('moneda', 'USD')
            
            simbolo_moneda = '
 if moneda == 'USD' else moneda
            
            # Crear mensaje
            content = f"💰 **¡GRAN DESCUENTO (-{descuento}%)!**"
            if self.rol_deals:
                content += f" <@&{self.rol_deals}>"
            
            # Crear embed
            color = self.colores_tienda.get(juego['tienda'], 0x00D9FF)
            
            embed = {
                "title": f"💸 {juego['titulo']}",
                "url": juego['url'],
                "color": color,
                "fields": [
                    {
                        "name": "🏪 Tienda",
                        "value": f"{juego.get('tienda_emoji', '')} {juego['tienda']}",
                        "inline": True
                    },
                    {
                        "name": "💰 Precio",
                        "value": f"~~{simbolo_moneda}{precio_regular:.2f}~~ → **{simbolo_moneda}{precio_actual:.2f}**",
                        "inline": True
                    },
                    {
                        "name": "📊 Descuento",
                        "value": f"**-{descuento}%**",
                        "inline": True
                    },
                    {
                        "name": "📊 Score HunDea",
                        "value": f"{score:.1f}/5.0 {estrellas}",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "HunDea v2.5 • Ofertas de Calidad"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Reviews si existen
            if juego.get('reviews_percent'):
                embed['fields'].append({
                    "name": "⭐ Reviews",
                    "value": f"{juego['reviews_percent']}% Positivas ({juego['reviews_count']:,} reviews)",
                    "inline": False
                })
            
            # Fecha de fin
            if juego.get('fecha_fin'):
                embed['fields'].append({
                    "name": "⏰ Disponible hasta",
                    "value": juego['fecha_fin'],
                    "inline": False
                })
            
            # Imagen
            if juego.get('imagen_url'):
                embed['image'] = {"url": juego['imagen_url']}
            
            # Enviar
            payload = {
                "content": content,
                "embeds": [embed]
            }
            
            response = requests.post(self.webhook_deals, json=payload)
            
            if response.status_code == 204:
                print(f"✅ Oferta enviada: {juego['titulo']} (-{descuento}%)")
                return True
            else:
                print(f"❌ Error al enviar oferta: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Error al enviar oferta: {e}")
            return False
    
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
