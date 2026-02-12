"""
Detector mejorado de juegos gratis de Epic Games
Con soporte para reviews
"""

import requests
from datetime import datetime

class EpicHunter:
    """
    Busca juegos gratis en Epic Games Store
    """
    
    def __init__(self):
        self.api_url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos gratis actuales de Epic
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos_gratis = []
        
        try:
            print("🔍 Consultando Epic Games Store...")
            response = requests.get(
                self.api_url, 
                params={'locale': 'es-ES', 'country': 'CO'}, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            elementos = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
            
            for juego in elementos:
                promociones = juego.get('promotions')
                if not promociones:
                    continue
                    
                ofertas = promociones.get('promotionalOffers', [])
                if not ofertas:
                    continue
                
                for oferta in ofertas:
                    for detalle in oferta.get('promotionalOffers', []):
                        precio = detalle.get('discountSetting', {}).get('discountPercentage', 0)
                        
                        if precio == 0:
                            info_juego = self._extraer_info_juego(juego, detalle)
                            if info_juego:
                                juegos_gratis.append(info_juego)
            
            print(f"✅ Epic: {len(juegos_gratis)} juego(s) gratis encontrados")
            return juegos_gratis
            
        except Exception as e:
            print(f"❌ Error al consultar Epic Games: {e}")
            return []
    
    def _extraer_info_juego(self, juego, detalle):
        """
        Extrae información del juego
        
        Args:
            juego (dict): Datos del juego
            detalle (dict): Detalles de la promoción
        
        Returns:
            dict: Información estructurada
        """
        try:
            # Construir URL del juego
            slug = ''
            mappings = juego.get('catalogNs', {}).get('mappings', [])
            if mappings:
                slug = mappings[0].get('pageSlug', '')
            
            if not slug:
                slug = juego.get('productSlug', '')
            
            info = {
                'id': f"epic_{juego.get('id', '')}",
                'titulo': juego.get('title', 'Sin título'),
                'descripcion': juego.get('description', 'Sin descripción'),
                'inicio': detalle.get('startDate'),
                'fin': detalle.get('endDate'),
                'url': f"https://store.epicgames.com/es-ES/p/{slug}" if slug else "https://store.epicgames.com/es-ES/free-games",
                'imagen': None,
                'tienda': 'Epic Games',
                'epic_id': juego.get('id', '')
            }
            
            # Buscar la mejor imagen
            imagenes = juego.get('keyImages', [])
            for img in imagenes:
                if img.get('type') in ['DieselStoreFrontWide', 'OfferImageWide']:
                    info['imagen'] = img.get('url')
                    break
            
            if not info['imagen'] and imagenes:
                info['imagen'] = imagenes[0].get('url')
            
            return info
            
        except Exception as e:
            print(f"❌ Error al extraer info del juego de Epic: {e}")
            return None
