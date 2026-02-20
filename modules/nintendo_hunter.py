"""
🎮 Nintendo Hunter - eShop
Busca juegos gratis y ofertas con descuento usando eShop (API pública)
"""

import re
import requests
from datetime import datetime


class NintendoHunter:
    """
    Busca deals de Nintendo eShop usando endpoints públicos
    """
    
    def __init__(self, region="MX", lang="es"):
        self.region = region
        self.lang = lang
        self.base_url = "https://ec.nintendo.com/api"
        self.session = requests.Session()
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos gratis de Nintendo eShop
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos = []
        
        try:
            print("🔍 Consultando Nintendo eShop (gratis)...")
            
            for item in self._iterar_sales():
                descuento = self._extraer_descuento(item)
                precio_actual = self._extraer_precio_actual(item)
                
                if not self._es_gratis(descuento, precio_actual):
                    continue
                
                info = self._crear_info_gratis(item)
                if info:
                    juegos.append(info)
            
            print(f"✅ Nintendo: {len(juegos)} juego(s) gratis encontrados")
            return juegos
            
        except Exception as e:
            print(f"❌ Error al consultar Nintendo eShop: {e}")
            return []
    
    def obtener_ofertas_descuento(self, descuento_minimo=30, descuento_maximo=99):
        """
        Obtiene ofertas con descuento de Nintendo eShop
        
        Args:
            descuento_minimo (int): % mínimo de descuento
            descuento_maximo (int): % máximo de descuento
        
        Returns:
            list: Lista de ofertas con descuento
        """
        ofertas = []
        
        try:
            print("🔍 Consultando Nintendo eShop (descuentos)...")
            
            for item in self._iterar_sales():
                descuento = self._extraer_descuento(item)
                if descuento is None:
                    continue
                
                if descuento < descuento_minimo:
                    continue
                if descuento > descuento_maximo:
                    continue
                
                info = self._crear_info_oferta(item, descuento)
                if info:
                    ofertas.append(info)
            
            print(f"✅ Nintendo: {len(ofertas)} oferta(s) encontradas")
            return ofertas
            
        except Exception as e:
            print(f"❌ Error al consultar Nintendo eShop: {e}")
            return []
    
    def _iterar_sales(self, count=60, max_pages=5):
        offset = 0
        paginas = 0
        
        while paginas < max_pages:
            data = self._buscar_sales(count=count, offset=offset)
            items = self._extraer_items(data)
            
            if not items:
                break
            
            for item in items:
                yield item
            
            if len(items) < count:
                break
            
            offset += count
            paginas += 1
    
    def _buscar_sales(self, count=60, offset=0):
        url = f"{self.base_url}/{self.region}/{self.lang}/search/sales"
        params = {"count": count, "offset": offset}
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                return {}
            return response.json()
        except Exception:
            return {}
    
    def _extraer_items(self, data):
        if not isinstance(data, dict):
            return []
        for key in ['contents', 'items', 'results', 'games']:
            items = data.get(key)
            if isinstance(items, list):
                return items
        return []
    
    def _extraer_descuento(self, item):
        for key in [
            'discount_rate', 'discountRate', 'discount', 'discount_percent',
            'discountPercentage', 'discount_percent_value'
        ]:
            if key in item:
                return self._parse_percent(item.get(key))
        
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['discount_rate', 'discount', 'discount_percent', 'discountPercentage']:
                if key in price:
                    return self._parse_percent(price.get(key))
            
            regular = self._parse_price(price.get('regular_price') or price.get('regular'))
            current = self._parse_price(price.get('discount_price') or price.get('sale_price') or price.get('current_price'))
            if regular and current is not None and regular > 0:
                return round(((regular - current) / regular) * 100, 1)
        
        return None
    
    def _extraer_precio_actual(self, item):
        for key in ['price_current', 'current_price', 'discount_price', 'sale_price']:
            if key in item:
                return self._parse_price(item.get(key))
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['discount_price', 'sale_price', 'current_price', 'current']:
                if key in price:
                    return self._parse_price(price.get(key))
        return None
    
    def _extraer_precio_regular(self, item):
        for key in ['price_regular', 'regular_price', 'original_price']:
            if key in item:
                return self._parse_price(item.get(key))
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['regular_price', 'original_price', 'regular']:
                if key in price:
                    return self._parse_price(price.get(key))
        return None
    
    def _extraer_moneda(self, item):
        for key in ['currency', 'currency_code', 'currencyCode']:
            value = item.get(key)
            if value:
                return value
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['currency', 'currency_code', 'currencyCode']:
                value = price.get(key)
                if value:
                    return value
        return 'MXN'
    
    def _extraer_url(self, item):
        for key in ['url', 'link', 'product_url', 'store_url']:
            value = item.get(key)
            if value:
                return value
        return None
    
    def _extraer_imagen(self, item):
        for key in ['image_url', 'image', 'img', 'picture']:
            value = item.get(key)
            if value:
                return value
        screenshots = item.get('screenshots')
        if isinstance(screenshots, list) and screenshots:
            return screenshots[0].get('url') or screenshots[0]
        return None
    
    def _extraer_fecha_fin(self, item):
        for key in ['end_date', 'endDate', 'sale_end', 'discount_ends_at']:
            value = item.get(key)
            if value:
                return value
        return None
    
    def _parse_percent(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            val = float(value)
            if 0 < val <= 1:
                return round(val * 100, 1)
            return abs(val)
        match = re.search(r"(-?\\d+(?:\\.\\d+)?)", str(value))
        if not match:
            return None
        val = float(match.group(1))
        if 0 < val <= 1:
            return round(val * 100, 1)
        return abs(val)
    
    def _parse_price(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"(\\d+(?:[\\.,]\\d+)?)", str(value))
        if not match:
            return None
        return float(match.group(1).replace(',', '.'))
    
    def _es_gratis(self, descuento, precio_actual):
        if descuento is not None and descuento >= 100:
            return True
        if precio_actual is not None and precio_actual == 0:
            return True
        return False
    
    def _crear_info_gratis(self, item):
        titulo = item.get('formal_name') or item.get('title') or item.get('name')
        if not titulo:
            return None
        
        product_id = item.get('nsuid') or item.get('id') or item.get('product_code') or titulo.replace(' ', '_')
        url = self._extraer_url(item) or "https://www.nintendo.com/es-mx/store/"
        imagen = self._extraer_imagen(item)
        descripcion = item.get('description') or item.get('short_description') or "Juego gratis de Nintendo"
        
        return {
            'id': f"nintendo_{product_id}",
            'titulo': titulo,
            'descripcion': descripcion[:200] if descripcion else "Juego gratis de Nintendo",
            'inicio': datetime.now().isoformat(),
            'fin': self._extraer_fecha_fin(item),
            'url': url,
            'imagen': imagen,
            'tienda': 'Nintendo eShop'
        }
    
    def _crear_info_oferta(self, item, descuento):
        titulo = item.get('formal_name') or item.get('title') or item.get('name')
        if not titulo:
            return None
        
        product_id = item.get('nsuid') or item.get('id') or item.get('product_code') or titulo.replace(' ', '_')
        url = self._extraer_url(item) or "https://www.nintendo.com/es-mx/store/"
        imagen = self._extraer_imagen(item)
        
        precio_actual = self._extraer_precio_actual(item)
        precio_regular = self._extraer_precio_regular(item)
        moneda = self._extraer_moneda(item)
        fecha_fin = self._extraer_fecha_fin(item)
        
        return {
            'id': f"nintendo_{product_id}",
            'titulo': titulo,
            'descripcion': item.get('description') or item.get('short_description') or "",
            'url': url,
            'imagen_url': imagen,
            'tienda': 'Nintendo eShop',
            'precio_actual': precio_actual if precio_actual is not None else 0,
            'precio_regular': precio_regular if precio_regular is not None else 0,
            'descuento_porcentaje': int(round(descuento)),
            'moneda': moneda,
            'fecha_fin': fecha_fin
        }


# Test
if __name__ == "__main__":
    hunter = NintendoHunter(region="MX", lang="es")
    juegos = hunter.obtener_juegos_gratis()
    ofertas = hunter.obtener_ofertas_descuento()
    print(f"\n🎮 Gratis: {len(juegos)} | Ofertas: {len(ofertas)}")
    for juego in juegos[:5]:
        print(f"  ✅ {juego['titulo']}")
    for oferta in ofertas[:5]:
        print(f"  💰 {oferta['titulo']} ({oferta.get('descuento_porcentaje', 0)}%)")
