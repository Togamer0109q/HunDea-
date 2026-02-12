"""
Detector de juegos gratis en Steam
"""

import requests
from datetime import datetime

class SteamHunter:
    """
    Busca y detecta juegos gratis en Steam
    """
    
    def __init__(self):
        self.base_url = "https://store.steampowered.com"
        self.api_url = "https://store.steampowered.com/api"
    
    def obtener_juegos_gratis(self):
        """
        Detecta juegos gratis en Steam
        
        Returns:
            list: Lista de juegos gratis encontrados
        """
        juegos_gratis = []
        
        try:
            # Intentar obtener juegos destacados
            featured_url = f"{self.api_url}/featuredcategories"
            response = requests.get(featured_url, timeout=10)
            
            if response.status_code != 200:
                print("⚠️ No se pudo acceder a Steam API")
                return juegos_gratis
            
            data = response.json()
            
            # Buscar en diferentes categorías
            categorias = ['specials', 'coming_soon', 'top_sellers']
            
            for categoria in categorias:
                if categoria in data and 'items' in data[categoria]:
                    for item in data[categoria]['items']:
                        # Verificar si es gratis
                        if self._es_gratis(item):
                            info_juego = self._extraer_info_juego(item)
                            if info_juego:
                                juegos_gratis.append(info_juego)
            
            print(f"✅ Steam: {len(juegos_gratis)} juego(s) gratis encontrados")
            
        except Exception as e:
            print(f"❌ Error al consultar Steam: {e}")
        
        return juegos_gratis
    
    def obtener_free_weekends(self):
        """
        Detecta Free Weekends en Steam
        
        Returns:
            list: Lista de juegos con Free Weekend
        """
        free_weekends = []
        
        try:
            # Esta funcionalidad requeriría scraping o una API específica
            # Por ahora retornamos lista vacía
            print("ℹ️ Free Weekends de Steam: Requiere implementación adicional")
            
        except Exception as e:
            print(f"❌ Error al buscar Free Weekends: {e}")
        
        return free_weekends
    
    def obtener_reviews(self, appid):
        """
        Obtiene las reviews de un juego de Steam
        
        Args:
            appid (str): ID del juego en Steam
        
        Returns:
            dict: Información de reviews
        """
        try:
            reviews_url = f"{self.base_url}/appreviews/{appid}"
            params = {
                'json': 1,
                'language': 'all',
                'purchase_type': 'all',
                'num_per_page': 0
            }
            
            response = requests.get(reviews_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'query_summary' not in data:
                return None
            
            summary = data['query_summary']
            
            total = summary.get('total_reviews', 0)
            positive = summary.get('total_positive', 0)
            
            if total and total > 0:
                percent = (positive / total) * 100
                return {
                    'reviews_count': total,
                    'reviews_percent': round(percent, 1),
                    'reviews_positive': positive,
                    'reviews_negative': total - positive
                }
            
        except Exception as e:
            print(f"❌ Error al obtener reviews de Steam: {e}")
        
        return None
    
    def _es_gratis(self, item):
        """
        Verifica si un juego es gratis
        
        Args:
            item (dict): Información del juego
        
        Returns:
            bool: True si es gratis
        """
        # Verificar descuento del 100%
        discount = item.get('discount_percent')
        if discount and discount == 100:
            return True
        
        # Verificar precio final 0
        final_price = item.get('final_price')
        original_price = item.get('original_price')
        
        if final_price is not None and final_price == 0:
            # Pero no si es F2P permanente
            if original_price is not None and original_price > 0:
                return True
        
        return False
    
    def _extraer_info_juego(self, item):
        """
        Extrae información del juego
        
        Args:
            item (dict): Datos del juego de Steam
        
        Returns:
            dict: Información estructurada
        """
        try:
            appid = item.get('id')
            
            if not appid:
                return None
            
            info = {
                'id': f"steam_{appid}",
                'titulo': item.get('name', 'Sin título'),
                'descripcion': item.get('headline', 'Sin descripción'),
                'url': f"https://store.steampowered.com/app/{appid}",
                'imagen': item.get('large_capsule_image', item.get('header_image')),
                'tienda': 'Steam',
                'inicio': None,
                'fin': None,  # Steam no siempre indica fecha de fin
                'appid': appid
            }
            
            # Obtener reviews
            reviews = self.obtener_reviews(appid)
            if reviews:
                info.update(reviews)
            
            return info
            
        except Exception as e:
            print(f"❌ Error al extraer info del juego: {e}")
            return None
