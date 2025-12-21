"""
🌟 IsThereAnyDeal Hunter
Detector de juegos gratis usando IsThereAnyDeal API
Detecta ofertas de múltiples tiendas: Steam, GOG, Humble, Epic, Uplay, etc.

API completamente gratuita, sin necesidad de API key
"""

import requests
from datetime import datetime
import time

class IsThereAnyDealHunter:
    """
    Busca juegos gratis en múltiples tiendas usando IsThereAnyDeal API v2
    """
    
    def __init__(self):
        self.base_url = "https://api.isthereanydeal.com"
        
        # Mapeo de tiendas por ID
        self.tiendas_map = {
            'steam': {'nombre': 'Steam', 'emoji': '🔵'},
            'gog': {'nombre': 'GOG', 'emoji': '🟣'},
            'humblestore': {'nombre': 'Humble Store', 'emoji': '🟠'},
            'epicgames': {'nombre': 'Epic Games', 'emoji': '⚫'},
            'itchio': {'nombre': 'Itch.io', 'emoji': '🔴'},
            'microsoft': {'nombre': 'Microsoft Store', 'emoji': '🟢'},
            'origin': {'nombre': 'EA Origin', 'emoji': '🟠'},
            'uplay': {'nombre': 'Ubisoft Connect', 'emoji': '🔵'},
            'nuuvem': {'nombre': 'Nuuvem', 'emoji': '🟡'},
            'greenmangaming': {'nombre': 'Green Man Gaming', 'emoji': '🟢'},
            'fanatical': {'nombre': 'Fanatical', 'emoji': '🔴'},
            'gamesplanet': {'nombre': 'Gamesplanet', 'emoji': '🔵'},
            'gamersgate': {'nombre': 'GamersGate', 'emoji': '🟣'}
        }
        
        # Estas tiendas suelen tener juegos gratis o promos permanentes
        self.tiendas_prioritarias = [
            'steam', 'gog', 'epicgames', 'itchio', 
            'humblestore', 'microsoft'
        ]
        
        print("\n🌟 IsThereAnyDeal Hunter inicializado")
        print(f"   📍 Monitoreando {len(self.tiendas_prioritarias)} tiendas principales")
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos que están 100% gratis (precio = $0)
        
        Strategy:
        1. Buscar deals recientes con precio actual = 0
        2. Verificar que sean verdaderamente gratis (no beta access)
        3. Filtrar duplicados entre tiendas
        
        Returns:
            list: Lista de juegos gratis encontrados
        """
        return self._buscar_juegos(tipo='gratis')
    
    def obtener_ofertas_descuento(self, descuento_minimo=70):
        """
        Obtiene juegos con descuentos significativos
        
        Args:
            descuento_minimo (int): Porcentaje mínimo de descuento (default: 70%)
        
        Returns:
            list: Lista de ofertas con descuento
        """
        return self._buscar_juegos(tipo='descuento', descuento_min=descuento_minimo)
    
    def _buscar_juegos(self, tipo='gratis', descuento_min=70):
        """
        Busca juegos (gratis o con descuento)
        
        Args:
            tipo (str): 'gratis' o 'descuento'
            descuento_min (int): Porcentaje mínimo de descuento
        
        Returns:
            list: Lista de juegos encontrados
        """
        juegos_encontrados = []
        
        try:
            if tipo == 'gratis':
                print("\n🔍 Consultando IsThereAnyDeal API (juegos gratis)...")
            else:
                print(f"\n💰 Consultando IsThereAnyDeal API (descuentos {descuento_min}%+)...")
            
            # Buscar en las tiendas prioritarias
            for tienda_id in self.tiendas_prioritarias:
                print(f"   🏪 Revisando {self.tiendas_map[tienda_id]['nombre']}...")
                
                juegos = self._buscar_en_tienda(tienda_id, tipo=tipo, descuento_min=descuento_min)
                
                if juegos:
                    tipo_texto = "gratis" if tipo == 'gratis' else f"con {descuento_min}%+ descuento"
                    print(f"      ✅ Encontrados {len(juegos)} juego(s) {tipo_texto}")
                    juegos_encontrados.extend(juegos)
                    
                # Rate limiting: pequeña pausa entre requests
                time.sleep(0.5)
            
            # Eliminar duplicados (mismo juego en diferentes tiendas)
            juegos_unicos = self._eliminar_duplicados(juegos_encontrados)
            
            if juegos_unicos:
                tipo_texto = "gratis" if tipo == 'gratis' else f"con descuento"
                print(f"\n✨ Total IsThereAnyDeal: {len(juegos_unicos)} juego(s) {tipo_texto} únicos")
            else:
                tipo_texto = "gratis" if tipo == 'gratis' else "con descuento"
                print(f"\n💤 IsThereAnyDeal: No hay juegos {tipo_texto} nuevos")
            
            return juegos_unicos
        
        except Exception as e:
            print(f"\n❌ Error en IsThereAnyDeal: {e}")
            return []
    
    def _buscar_en_tienda(self, tienda_id, tipo='gratis', descuento_min=70):
        """
        Busca juegos en una tienda específica
        
        Args:
            tienda_id (str): ID de la tienda
            tipo (str): 'gratis' o 'descuento'
            descuento_min (int): Porcentaje mínimo de descuento
        
        Returns:
            list: Juegos encontrados
        """
        juegos = []
        
        try:
            # ITAD API v2: Buscar deals con precio 0
            url = f"{self.base_url}/v02/web/search/"
            
            params = {
                'q': '',  # Búsqueda vacía para obtener todos
                'region': 'us',
                'country': 'US',
                'shops': tienda_id,
                'offset': 0,
                'limit': 20  # Limitar resultados
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                return juegos
            
            data = response.json()
            
            # Procesar resultados
            if 'data' in data and 'list' in data['data']:
                for item in data['data']['list']:
                    # Buscar la mejor oferta actual
                    if 'deals' in item and item['deals']:
                        mejor_deal = min(item['deals'], key=lambda x: x.get('price', {}).get('amount', float('inf')))
                        
                        precio_actual = mejor_deal.get('price', {}).get('amount', 999)
                        precio_regular = mejor_deal.get('regular', {}).get('amount', 999)
                        descuento = mejor_deal.get('cut', 0)
                        
                        # Filtrar según el tipo
                        agregar = False
                        
                        if tipo == 'gratis' and precio_actual == 0:
                            agregar = True
                        elif tipo == 'descuento' and descuento >= descuento_min and precio_actual > 0:
                            agregar = True
                        
                        if agregar:
                            juego_info = self._extraer_info_juego(item, mejor_deal, tienda_id, tipo=tipo)
                            if juego_info:
                                juegos.append(juego_info)
        
        except requests.Timeout:
            print(f"      ⚠️ Timeout en {tienda_id}")
        except Exception as e:
            print(f"      ⚠️ Error en {tienda_id}: {str(e)[:50]}")
        
        return juegos
    
    def _extraer_info_juego(self, item, deal, tienda_id, tipo='gratis'):
        """
        Extrae información del juego en formato estándar
        
        Args:
            item (dict): Datos del juego de ITAD
            deal (dict): Datos del deal
            tienda_id (str): ID de la tienda
            tipo (str): 'gratis' o 'descuento'
        
        Returns:
            dict: Información del juego o None
        """
        try:
            titulo = item.get('title', 'Juego sin título')
            
            # ID único del juego
            game_id = item.get('id', '')
            if not game_id:
                return None
            
            # URL del deal
            url_deal = deal.get('url', '')
            if not url_deal:
                return None
            
            # Fecha de fin (si existe)
            fecha_fin = None
            if 'expiry' in deal:
                try:
                    timestamp = deal['expiry']
                    if timestamp:
                        fecha_fin = datetime.fromtimestamp(timestamp)
                except:
                    pass
            
            # Info de la tienda
            tienda_info = self.tiendas_map.get(tienda_id, {
                'nombre': tienda_id.title(),
                'emoji': '🏪'
            })
            
            # Información de precio (para descuentos)
            precio_info = {}
            if tipo == 'descuento':
                precio_info = {
                    'precio_actual': deal.get('price', {}).get('amount', 0),
                    'precio_regular': deal.get('regular', {}).get('amount', 0),
                    'descuento_porcentaje': deal.get('cut', 0),
                    'moneda': deal.get('price', {}).get('currency', 'USD')
                }
            
            juego_base = {
                'id': f"itad_{tienda_id}_{game_id}",
                'titulo': titulo,
                'tienda': tienda_info['nombre'],
                'tienda_emoji': tienda_info['emoji'],
                'url': url_deal,
                'fecha_fin': fecha_fin.strftime("%A, %d de %B de %Y a las %I:%M %p") if fecha_fin else "Sin fecha límite",
                'imagen_url': self._obtener_imagen(item),
                'tipo': tipo,
                'fuente': 'IsThereAnyDeal',
                # Sin reviews inicialmente (se buscarán luego con RAWG)
                'reviews_percent': None,
                'reviews_count': None,
                'metacritic': None
            }
            
            # Agregar info de precio si es descuento
            if tipo == 'descuento':
                juego_base.update(precio_info)
            
            return juego_base
        
        except Exception as e:
            print(f"         ⚠️ Error al extraer info: {str(e)[:50]}")
            return None
    
    def _obtener_imagen(self, item):
        """
        Obtiene URL de imagen del juego
        
        Args:
            item (dict): Datos del juego
        
        Returns:
            str: URL de la imagen o None
        """
        # ITAD proporciona imágenes en diferentes tamaños
        if 'assets' in item:
            assets = item['assets']
            
            # Prioridad: banner, cover, logo
            for tipo in ['banner600', 'cover', 'logo']:
                if tipo in assets and assets[tipo]:
                    return assets[tipo]
        
        return None
    
    def _eliminar_duplicados(self, juegos):
        """
        Elimina juegos duplicados (mismo título, diferentes tiendas)
        Prioriza por: 1) Epic Games, 2) GOG, 3) Steam, 4) Otras
        
        Args:
            juegos (list): Lista de juegos
        
        Returns:
            list: Lista sin duplicados
        """
        if not juegos:
            return []
        
        # Prioridad de tiendas
        prioridad = {
            'Epic Games': 1,
            'GOG': 2,
            'Steam': 3,
            'Microsoft Store': 4,
            'Humble Store': 5
        }
        
        # Agrupar por título (normalizado)
        por_titulo = {}
        
        for juego in juegos:
            titulo_norm = juego['titulo'].lower().strip()
            
            if titulo_norm not in por_titulo:
                por_titulo[titulo_norm] = juego
            else:
                # Mantener el de mejor tienda
                tienda_actual = por_titulo[titulo_norm]['tienda']
                tienda_nueva = juego['tienda']
                
                prioridad_actual = prioridad.get(tienda_actual, 999)
                prioridad_nueva = prioridad.get(tienda_nueva, 999)
                
                if prioridad_nueva < prioridad_actual:
                    por_titulo[titulo_norm] = juego
        
        return list(por_titulo.values())
    
    def verificar_disponibilidad(self, game_id):
        """
        Verifica si un juego específico está gratis
        
        Args:
            game_id (str): ID del juego en ITAD
        
        Returns:
            dict: Info actualizada o None
        """
        try:
            url = f"{self.base_url}/v02/game/prices/"
            
            params = {
                'key': game_id,
                'region': 'us',
                'country': 'US'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Buscar ofertas con precio 0
            if 'data' in data:
                for tienda_id, tienda_data in data['data'].items():
                    if isinstance(tienda_data, dict):
                        price = tienda_data.get('price', {}).get('amount', 999)
                        
                        if price == 0:
                            return {
                                'disponible': True,
                                'tienda': self.tiendas_map.get(tienda_id, {}).get('nombre', tienda_id),
                                'url': tienda_data.get('url', ''),
                                'expiracion': tienda_data.get('expiry')
                            }
            
            return None
        
        except Exception as e:
            print(f"⚠️ Error al verificar disponibilidad: {e}")
            return None


# Función helper para testing
def test_itad():
    """Prueba rápida del hunter"""
    print("\n" + "="*70)
    print("🧪 TEST - IsThereAnyDeal Hunter")
    print("="*70)
    
    hunter = IsThereAnyDealHunter()
    juegos = hunter.obtener_juegos_gratis()
    
    if juegos:
        print(f"\n📊 Resultados:")
        for juego in juegos:
            print(f"\n🎮 {juego['titulo']}")
            print(f"   🏪 {juego['tienda']}")
            print(f"   🔗 {juego['url'][:60]}...")
            print(f"   ⏰ {juego['fecha_fin']}")
    else:
        print("\n❌ No se encontraron juegos gratis")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_itad()
