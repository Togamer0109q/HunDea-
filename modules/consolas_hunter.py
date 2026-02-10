"""
Módulo Hunter para Consolas (PlayStation, Xbox, Nintendo)
Busca ofertas y juegos gratis usando feeds de Reddit y otras fuentes RSS.
"""

import feedparser
import re
from datetime import datetime

class ConsolasHunter:
    """
    Caza ofertas de PlayStation, Xbox y Nintendo Switch
    """
    
    def __init__(self):
        # Feeds de Reddit (formato RSS)
        self.feeds = {
            'PlayStation': 'https://www.reddit.com/r/PS4Deals/new/.rss',
            'Xbox': 'https://www.reddit.com/r/XboxDeals/new/.rss',
            'Nintendo': 'https://www.reddit.com/r/NintendoSwitchDeals/new/.rss'
        }
        
        # Emojis por plataforma
        self.emojis = {
            'PlayStation': '🟦',
            'Xbox': '🟩',
            'Nintendo': '🟥'
        }
        
        # Colores para Discord
        self.colores = {
            'PlayStation': 0x003791,
            'Xbox': 0x107C10,
            'Nintendo': 0xE60012
        }

    def obtener_ofertas(self, limite=10):
        """
        Obtiene las últimas ofertas de las 3 plataformas
        """
        todas_ofertas = []
        
        for plataforma, url in self.feeds.items():
            print(f"   🎮 Buscando ofertas de {plataforma}...")
            try:
                feed = feedparser.parse(url)
                count = 0
                for entry in feed.entries:
                    if count >= limite:
                        break
                    
                    # Ignorar posts que no parecen ofertas (ej: discusiones)
                    if not self._es_oferta_valida(entry.title):
                        continue
                        
                    # Extraer precio y descuento si es posible
                    info_precio = self._extraer_info_precio(entry.title)
                    
                    juego = {
                        'id': f"cons_{entry.id.split('/')[-1]}", # ID único basado en Reddit
                        'titulo': self._limpiar_titulo(entry.title),
                        'tienda': plataforma,
                        'tienda_emoji': self.emojis.get(plataforma, '🎮'),
                        'url': entry.link,
                        'imagen_url': self._extraer_imagen(entry),
                        'descuento_porcentaje': info_precio.get('descuento', 0),
                        'precio_actual': info_precio.get('actual', 0),
                        'precio_regular': info_precio.get('regular', 0),
                        'moneda': 'USD', # Reddit suele estar en USD
                        'color': self.colores.get(plataforma, 0x00D9FF),
                        'tipo': 'gratis' if info_precio.get('gratis') else 'oferta'
                    }
                    
                    todas_ofertas.append(juego)
                    count += 1
                    
            except Exception as e:
                print(f"      ❌ Error en {plataforma}: {e}")
                
        return todas_ofertas

    def _es_oferta_valida(self, titulo):
        """Filtra títulos que no sean ofertas reales"""
        titulo_low = titulo.lower()
        # Debe contener un símbolo de moneda o la palabra 'free' o un porcentaje
        keywords = ['$', '€', 'free', '%', 'gratis', 'off']
        return any(k in titulo_low for k in keywords)

    def _limpiar_titulo(self, titulo):
        """Limpia el título de Reddit [Region] [Store] etc"""
        # Eliminar corchetes y su contenido: [PSN] [US] Game Title -> Game Title
        titulo = re.sub(r'\[[^\]]*\]', '', titulo)
        return titulo.strip()

    def _extraer_info_precio(self, titulo):
        """Intenta extraer precio y descuento del título"""
        info = {'gratis': False, 'descuento': 0, 'actual': 0, 'regular': 0}
        
        if 'free' in titulo.lower() or '100%' in titulo:
            info['gratis'] = True
            info['descuento'] = 100
            return info
            
        # Buscar porcentajes: 75% off
        pct = re.search(r'(\d+)%', titulo)
        if pct:
            info['descuento'] = int(pct.group(1))
            
        # Buscar precios: $19.99
        precios = re.findall(r'\$(\d+\.?\d*)', titulo)
        if len(precios) >= 1:
            info['actual'] = float(precios[0])
            if len(precios) >= 2:
                info['regular'] = float(precios[1])
                
        return info

    def _extraer_imagen(self, entry):
        """Intenta extraer una miniatura del feed de Reddit"""
        if 'media_thumbnail' in entry and entry.media_thumbnail:
            return entry.media_thumbnail[0]['url']
        # Buscar en el contenido HTML si hay un <img>
        img_match = re.search(r'<img [^>]*src="([^"]+)"', entry.summary)
        if img_match:
            return img_match.group(1)
        return None
