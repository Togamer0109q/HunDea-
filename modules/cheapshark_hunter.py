"""
🦈 CheapShark Hunter
Detector de ofertas usando CheapShark API
Encuentra juegos gratis y ofertas increíbles
"""

import requests
import time

class CheapSharkHunter:
    """
    Busca juegos gratis y ofertas en múltiples tiendas usando CheapShark
    """
    
    def __init__(self):
        self.base_url = "https://www.cheapshark.com/api/1.0"
        
        # Mapeo de tiendas (CheapShark IDs)
        self.tiendas_map = {
            '1': {'nombre': 'Steam', 'emoji': '🔵'},
            '2': {'nombre': 'GamersGate', 'emoji': '🟣'},
            '3': {'nombre': 'GreenManGaming', 'emoji': '🟢'},
            '7': {'nombre': 'GOG', 'emoji': '🟣'},
            '8': {'nombre': 'Origin', 'emoji': '🟠'},
            '11': {'nombre': 'Humble Store', 'emoji': '🟠'},
            '13': {'nombre': 'Uplay', 'emoji': '🔵'},
            '15': {'nombre': 'Fanatical', 'emoji': '🔴'},
            '25': {'nombre': 'Epic Games', 'emoji': '⚫'},
            '27': {'nombre': 'Gamesplanet', 'emoji': '🔵'},
            '28': {'nombre': 'Gamesload', 'emoji': '🟡'},
            '29': {'nombre': 'AllYouPlay', 'emoji': '🟢'},
            '30': {'nombre': 'DLGamer', 'emoji': '🟠'},
        }
        
        print("\n🦈 CheapShark Hunter inicializado")
        print(f"   📍 Monitoreando {len(self.tiendas_map)} tiendas")
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos completamente gratis (precio = $0)
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos = []
        
        try:
            print("\n🦈 Consultando CheapShark (juegos gratis)...")
            
            # Endpoint: juegos con precio máximo $0
            url = f"{self.base_url}/deals"
            params = {
                'upperPrice': 0,
                'pageSize': 60,
                'sortBy': 'recent'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ CheapShark respondió con {response.status_code}")
                return []
            
            data = response.json()
            
            for deal in data:
                juego_info = self._extraer_info_juego(deal, tipo='gratis')
                if juego_info:
                    juegos.append(juego_info)
            
            if juegos:
                print(f"   ✅ CheapShark: {len(juegos)} juego(s) gratis")
            else:
                print(f"   💤 CheapShark: No hay juegos gratis")
            
            return juegos
        
        except Exception as e:
            print(f"   ❌ Error en CheapShark: {e}")
            return []
    
    def obtener_ofertas_descuento(self, descuento_minimo=70, precio_maximo=10):
        """
        Obtiene ofertas con descuentos significativos
        
        Args:
            descuento_minimo (int): Porcentaje mínimo (default: 70%)
            precio_maximo (float): Precio máximo en USD (default: $10)
        
        Returns:
            list: Lista de ofertas
        """
        ofertas = []
        
        try:
            print(f"\n🦈 Consultando CheapShark (ofertas {descuento_minimo}%+)...")
            
            url = f"{self.base_url}/deals"
            params = {
                'lowerPrice': 0,
                'upperPrice': precio_maximo,
                'onSale': 1,
                'pageSize': 60,
                'sortBy': 'Savings'  # Ordenar por mayor descuento
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ CheapShark respondió con {response.status_code}")
                return []
            
            data = response.json()
            
            # Filtrar por descuento mínimo
            for deal in data:
                descuento = float(deal.get('savings', '0'))
                if descuento >= descuento_minimo:
                    juego_info = self._extraer_info_juego(deal, tipo='descuento')
                    if juego_info:
                        ofertas.append(juego_info)
            
            if ofertas:
                print(f"   ✅ CheapShark: {len(ofertas)} oferta(s)")
            else:
                print(f"   💤 CheapShark: No hay ofertas {descuento_minimo}%+")
            
            return ofertas
        
        except Exception as e:
            print(f"   ❌ Error en CheapShark: {e}")
            return []
    
    def _extraer_info_juego(self, deal, tipo='gratis'):
        """
        Extrae información del juego en formato estándar
        
        Args:
            deal (dict): Datos del deal de CheapShark
            tipo (str): 'gratis' o 'descuento'
        
        Returns:
            dict: Información del juego
        """
        try:
            titulo = deal.get('title', 'Juego sin título')
            
            # ID único
            deal_id = deal.get('dealID', '')
            if not deal_id:
                return None
            
            # Tienda
            store_id = deal.get('storeID', '1')
            tienda_info = self.tiendas_map.get(store_id, {
                'nombre': f'Tienda {store_id}',
                'emoji': '🏪'
            })
            
            # Precios
            precio_actual = float(deal.get('salePrice', '0'))
            precio_regular = float(deal.get('normalPrice', '0'))
            descuento = int(float(deal.get('savings', '0')))
            
            # URL (CheapShark redirect)
            url = f"https://www.cheapshark.com/redirect?dealID={deal_id}"
            
            # Rating de Steam (si existe)
            steam_rating = deal.get('steamRatingPercent', None)
            steam_reviews = deal.get('steamRatingCount', None)
            
            # Fecha de fin (timestamp)
            fecha_fin = None
            if deal.get('lastChange'):
                fecha_fin = "Tiempo limitado"
            
            # Thumbnail
            imagen_url = None
            if deal.get('thumb'):
                imagen_url = deal['thumb']
            
            juego_base = {
                'id': f"cheapshark_{deal_id}",
                'titulo': titulo,
                'tienda': tienda_info['nombre'],
                'tienda_emoji': tienda_info['emoji'],
                'url': url,
                'fecha_fin': fecha_fin or "Sin fecha límite",
                'imagen_url': imagen_url,
                'tipo': tipo,
                'fuente': 'CheapShark',
                'metacritic': int(deal.get('metacriticScore', 0)) if deal.get('metacriticScore') else None
            }
            
            # Agregar reviews de Steam si existen
            if steam_rating and steam_reviews:
                juego_base['reviews_percent'] = int(steam_rating)
                juego_base['reviews_count'] = int(steam_reviews)
            else:
                juego_base['reviews_percent'] = None
                juego_base['reviews_count'] = None
            
            # Agregar info de precio si es descuento
            if tipo == 'descuento':
                juego_base['precio_actual'] = precio_actual
                juego_base['precio_regular'] = precio_regular
                juego_base['descuento_porcentaje'] = descuento
                juego_base['moneda'] = 'USD'
            
            return juego_base
        
        except Exception as e:
            print(f"      ⚠️ Error al extraer info: {str(e)[:50]}")
            return None


# Test function
def test_cheapshark():
    """Prueba rápida del hunter"""
    print("\n" + "="*70)
    print("🧪 TEST - CheapShark Hunter")
    print("="*70)
    
    hunter = CheapSharkHunter()
    
    # Test 1: Juegos gratis
    print("\n📦 Test 1: Juegos gratis")
    juegos = hunter.obtener_juegos_gratis()
    
    if juegos:
        print(f"\n✅ Encontrados {len(juegos)} juego(s) gratis")
        for juego in juegos[:3]:  # Mostrar solo primeros 3
            print(f"\n🎮 {juego['titulo']}")
            print(f"   🏪 {juego['tienda']}")
            print(f"   🔗 {juego['url'][:60]}...")
    
    # Test 2: Ofertas
    print("\n\n📦 Test 2: Ofertas con 70%+ descuento")
    ofertas = hunter.obtener_ofertas_descuento(70, 10)
    
    if ofertas:
        print(f"\n✅ Encontradas {len(ofertas)} oferta(s)")
        for oferta in ofertas[:3]:  # Mostrar solo primeras 3
            print(f"\n💰 {oferta['titulo']}")
            print(f"   🏪 {oferta['tienda']}")
            print(f"   💸 ${oferta['precio_actual']:.2f} (era ${oferta['precio_regular']:.2f})")
            print(f"   📊 -{oferta['descuento_porcentaje']}% descuento")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_cheapshark()
