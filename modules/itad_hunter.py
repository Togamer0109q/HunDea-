"""
Detector de juegos gratis usando IsThereAnyDeal API
Detecta ofertas de múltiples tiendas: Steam, GOG, Humble, Epic, etc.
"""

import requests
from datetime import datetime

class IsThereAnyDealHunter:
    """
    Busca juegos gratis en múltiples tiendas usando IsThereAnyDeal
    """
    
    def __init__(self):
        # IsThereAnyDeal API es completamente gratuita y no requiere key
        self.base_url = "https://api.isthereanydeal.com"
        
        # Mapeo de tiendas
        self.tiendas_conocidas = {
            'steam': 'Steam',
            'gog': 'GOG',
            'humblestore': 'Humble Store',
            'epicgames': 'Epic Games',
            'itchio': 'Itch.io',
            'microsoft': 'Microsoft Store',
            'origin': 'EA Origin',
            'uplay': 'Ubisoft Connect'
        }
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos que están 100% gratis
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos_gratis = []
        
        try:
            print("🔍 Consultando IsThereAnyDeal...")
            
            # ITAD no tiene endpoint directo de "free games"
            # Vamos a usar una estrategia diferente: buscar ofertas con precio 0
            
            # Por ahora, implementación básica
            # En producción, necesitaríamos mantener una lista de juegos conocidos
            # y verificar sus precios
            
            print("ℹ️ IsThereAnyDeal: Implementación en progreso")
            print("💡 Por ahora, Epic Games es la fuente principal")
            
        except Exception as e:
            print(f"❌ Error al consultar IsThereAnyDeal: {e}")
        
        return juegos_gratis
    
    def verificar_precio(self, game_id):
        """
        Verifica el precio actual de un juego
        
        Args:
            game_id (str): ID del juego en ITAD
        
        Returns:
            dict: Info de precios o None
        """
        try:
            url = f"{self.base_url}/games/prices/v2"
            params = {
                'key': game_id,
                'country': 'US'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Buscar ofertas con precio 0
            if 'data' in data:
                for offer in data['data'].get('list', []):
                    if offer.get('price_new', 0) == 0:
                        return {
                            'tienda': self.tiendas_conocidas.get(offer.get('shop', {}).get('id', ''), 'Desconocida'),
                            'url': offer.get('url', ''),
                            'fin': offer.get('price_cut_until')
                        }
            
        except Exception as e:
            print(f"⚠️ Error al verificar precio: {e}")
        
        return None
