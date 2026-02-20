"""
Detector de juegos gratis en Steam
"""

import re
import requests
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

class SteamHunter:
    """
    Busca y detecta juegos gratis en Steam
    """
    
    def __init__(self, cc="us", lang="english"):
        self.base_url = "https://store.steampowered.com"
        self.api_url = "https://store.steampowered.com/api"
        self.session = requests.Session()
        self.cc = cc
        self.lang = lang
    
    def obtener_juegos_gratis(self):
        """
        Detecta juegos gratis en Steam
        
        Returns:
            list: Lista de juegos gratis encontrados
        """
        juegos_gratis = []
        
        try:
            # Intentar obtener juegos destacados
            data = self._obtener_featured_categories()
            if not data:
                print("⚠️ No se pudo acceder a Steam API")
                return juegos_gratis
            
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
            data = self._obtener_featured_categories()
            if not data:
                print("⚠️ No se pudo obtener featured categories de Steam")
                return free_weekends

            spotlights = self._extraer_spotlights(data)

            # Buscar items con nombre "Free Weekend"
            free_items = []
            for item in spotlights:
                name = (item.get('name') or '').lower()
                if 'free weekend' in name:
                    free_items.append(item)

            if not free_items:
                print("ℹ️ No se encontraron Free Weekends en Steam (spotlights)")
                return free_weekends

            vistos = set()
            for item in free_items:
                url = item.get('url', '')
                appid = self._extraer_appid(url)
                if not appid:
                    continue
                if appid in vistos:
                    continue
                vistos.add(appid)

                info = self._obtener_detalles_app(appid)
                if not info:
                    continue
                if info.get('es_f2p'):
                    # Evitar F2P permanentes
                    continue
                if info.get('tipo_app') and info.get('tipo_app') != 'game':
                    continue

                # Estimar fin del free weekend para deduplicación (no se muestra)
                info['fin_ts_estimada'] = self._estimar_fin_free_weekend_ts()
                info['tipo'] = 'free_weekend'

                # Reviews
                reviews = self.obtener_reviews(appid)
                if reviews:
                    info.update(reviews)

                free_weekends.append(info)

            print(f"✅ Steam: {len(free_weekends)} Free Weekend(s) encontrados")
            
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
            
            response = self.session.get(reviews_url, params=params, timeout=10)
            
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

    def _obtener_featured_categories(self, cc=None, lang=None):
        """
        Obtiene featured categories de Steam (incluye spotlights)
        """
        try:
            url = f"{self.api_url}/featuredcategories"
            params = {"cc": cc or self.cc, "l": lang or self.lang}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None

    def _extraer_spotlights(self, data):
        """
        Extrae items de spotlight del response de featured categories
        """
        spotlights = []
        try:
            for value in data.values():
                if isinstance(value, dict) and value.get('id') == 'cat_spotlight':
                    items = value.get('items', [])
                    if isinstance(items, list):
                        spotlights.extend(items)
        except Exception:
            pass
        return spotlights

    def _extraer_appid(self, url):
        """
        Extrae el appid de una URL de Steam
        """
        if not url:
            return None
        match = re.search(r"/app/(\d+)", url)
        if match:
            return match.group(1)
        match = re.search(r"[?&]appid=(\d+)", url)
        if match:
            return match.group(1)
        return None

    def _obtener_detalles_app(self, appid, cc=None, lang=None):
        """
        Obtiene detalles del app desde appdetails
        """
        try:
            url = f"{self.api_url}/appdetails"
            params = {"appids": appid, "cc": cc or self.cc, "l": lang or self.lang}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            data = response.json()
            app_data = data.get(str(appid), {})
            if not app_data.get('success'):
                return None
            info = app_data.get('data', {})

            titulo = info.get('name', f"App {appid}")
            descripcion = info.get('short_description', '') or info.get('about_the_game', '')
            imagen = info.get('header_image')
            store_url = f"{self.base_url}/app/{appid}"
            es_f2p = bool(info.get('is_free', False))
            tipo_app = info.get('type')

            return {
                'id': f"steam_{appid}",
                'titulo': titulo,
                'descripcion': descripcion,
                'url': store_url,
                'imagen': imagen,
                'tienda': 'Steam',
                'inicio': None,
                'fin': None,
                'appid': appid,
                'es_f2p': es_f2p,
                'tipo_app': tipo_app
            }
        except Exception:
            return None

    def _estimar_fin_free_weekend_ts(self, now=None):
        """
        Estima el fin del Free Weekend (lunes 10:00 PT) para deduplicación
        """
        try:
            if ZoneInfo:
                tz = ZoneInfo("America/Los_Angeles")
                now_tz = now.astimezone(tz) if now else datetime.now(tz)
            else:
                now_tz = now or datetime.utcnow().replace(tzinfo=timezone.utc)

            weekday = now_tz.weekday()  # Monday=0
            days_ahead = (7 - weekday) % 7
            end_dt = (now_tz + timedelta(days=days_ahead)).replace(
                hour=10, minute=0, second=0, microsecond=0
            )
            if days_ahead == 0 and now_tz >= end_dt:
                end_dt = end_dt + timedelta(days=7)

            return int(end_dt.astimezone(timezone.utc).timestamp())
        except Exception:
            return int(datetime.utcnow().timestamp()) + (4 * 24 * 60 * 60)
