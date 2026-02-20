"""
🎮 PlatPrices Hunter - PlayStation Deals
Busca deals y juegos gratis de PlayStation usando PlatPrices (endpoints públicos)
"""

import re
import requests
from datetime import datetime


class PlatPricesHunter:
    """
    Busca deals de PlayStation (PS4/PS5) usando PlatPrices
    """
    
    def __init__(self, api_key=None, region="en-us"):
        self.api_key = api_key or "GH28jbaLCoVsO5QlNHnV8fHpvsQnuUbB"
        self.base_url = "https://platprices.com"
        self.region = region
        self.session = requests.Session()
        self._region_real = region
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos gratis de PlayStation
        
        Returns:
            list: Lista de juegos gratis de PS
        """
        juegos_gratis = []
        
        try:
            print("🔍 Consultando PlatPrices (PlayStation gratis)...")
            sales = self._obtener_sales()
            
            # Extraer items gratis desde sales/items
            for sale in sales:
                items = self._obtener_items_sale(sale)
                if not items:
                    continue
                
                for item in items:
                    descuento = self._extraer_descuento(item)
                    precio_actual = self._extraer_precio_actual(item)
                    
                    if not self._es_gratis(descuento, precio_actual):
                        continue
                    
                    info = self._crear_info_gratis(item)
                    if info:
                        juegos_gratis.append(info)
            
            # Fallback: PS Plus Essential (si no hay items)
            if not juegos_gratis:
                juegos_gratis.extend(self._fallback_ps_plus(sales))
            
            print(f"✅ PlatPrices: {len(juegos_gratis)} juego(s) gratis encontrados")
            return juegos_gratis
            
        except Exception as e:
            print(f"❌ Error al consultar PlatPrices: {e}")
            return []
    
    def obtener_ofertas_descuento(self, descuento_minimo=30, descuento_maximo=99):
        """
        Obtiene ofertas con descuento de PlayStation
        
        Args:
            descuento_minimo (int): % mínimo de descuento
            descuento_maximo (int): % máximo de descuento (99 por defecto)
        
        Returns:
            list: Lista de ofertas con descuento
        """
        ofertas = []
        
        try:
            print("🔍 Consultando PlatPrices (PlayStation descuentos)...")
            sales = self._obtener_sales()
            
            for sale in sales:
                items = self._obtener_items_sale(sale)
                if not items:
                    continue
                
                for item in items:
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
            
            print(f"✅ PlatPrices: {len(ofertas)} oferta(s) de PlayStation encontradas")
            return ofertas
            
        except Exception as e:
            print(f"❌ Error al consultar PlatPrices: {e}")
            return []
    
    def _obtener_sales(self):
        try:
            data = self._get_json(self._sales_url(self.region))
            self._region_real = self.region
            if not data and self.region != "en-us":
                data = self._get_json(self._sales_url("en-us"))
                if data:
                    self._region_real = "en-us"
            if not data:
                return []
            sales = data.get('sales', [])
            return sales if isinstance(sales, list) else []
        except Exception:
            return []

    def _sales_url(self, region):
        return f"{self.base_url}/{region}/sales.json"
    
    def _obtener_items_sale(self, sale):
        """
        Extrae items de una sale. Si no están incluidos, intenta endpoints de detalle.
        """
        items = self._extraer_items(sale)
        if items:
            return items
        
        sale_id = sale.get('id') or sale.get('sale_id')
        if not sale_id:
            return []
        
        # Intentar endpoints de detalle (tolerante a cambios)
        region = self._region_real or self.region
        posibles = [
            f"{self.base_url}/{region}/sale/{sale_id}.json",
            f"{self.base_url}/{region}/sales/{sale_id}.json",
            f"{self.base_url}/{region}/sale/{sale_id}",
            f"{self.base_url}/{region}/sales/{sale_id}",
        ]
        
        for url in posibles:
            data = self._get_json(url)
            if not data:
                continue
            items = self._extraer_items(data)
            if items:
                return items
        
        return []
    
    def _extraer_items(self, data):
        if not isinstance(data, dict):
            return []
        for key in ['items', 'products', 'games', 'titles', 'results']:
            items = data.get(key)
            if isinstance(items, list):
                return items
        sale = data.get('sale')
        if isinstance(sale, dict):
            for key in ['items', 'products', 'games', 'titles', 'results']:
                items = sale.get(key)
                if isinstance(items, list):
                    return items
        return []
    
    def _get_json(self, url):
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None
    
    def _extraer_descuento(self, item):
        for key in [
            'discount_percent', 'discountPercent', 'discount', 'discount_pct',
            'percentage_off', 'percent_off', 'percentOff', 'discountPercentage'
        ]:
            if key in item:
                return self._parse_percent(item.get(key))
        
        price = item.get('price') or item.get('prices')
        if isinstance(price, dict):
            for key in ['discount', 'discount_percent', 'discountPercent', 'percent_off', 'percentage_off']:
                if key in price:
                    return self._parse_percent(price.get(key))
        
        return None
    
    def _extraer_precio_actual(self, item):
        for key in ['price_current', 'current_price', 'price', 'sale_price', 'price_new', 'currentPrice']:
            if key in item:
                return self._parse_price(item.get(key))
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['current', 'sale', 'value', 'amount']:
                if key in price:
                    return self._parse_price(price.get(key))
        return None
    
    def _extraer_precio_regular(self, item):
        for key in ['price_regular', 'regular_price', 'original_price', 'price_old', 'listPrice']:
            if key in item:
                return self._parse_price(item.get(key))
        price = item.get('price')
        if isinstance(price, dict):
            for key in ['regular', 'original', 'list', 'base']:
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
        return 'USD'
    
    def _parse_percent(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"(-?\\d+(?:\\.\\d+)?)", str(value))
        if not match:
            return None
        return abs(float(match.group(1)))
    
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
        titulo = item.get('title') or item.get('name') or item.get('productName')
        if not titulo:
            return None
        
        product_id = item.get('id') or item.get('product_id') or item.get('slug') or titulo.replace(' ', '_')
        url = item.get('url') or item.get('store_url') or item.get('product_url')
        imagen = item.get('image') or item.get('image_url') or item.get('img')
        descripcion = item.get('description') or item.get('short_description') or "Juego gratis de PlayStation"
        
        return {
            'id': f"ps_{product_id}",
            'titulo': titulo,
            'descripcion': descripcion[:200] if descripcion else "Juego gratis de PlayStation",
            'inicio': datetime.now().isoformat(),
            'fin': None,
            'url': url or f"{self.base_url}/{self._region_real}/",
            'imagen': imagen,
            'tienda': 'PlayStation Store'
        }
    
    def _crear_info_oferta(self, item, descuento):
        titulo = item.get('title') or item.get('name') or item.get('productName')
        if not titulo:
            return None
        
        product_id = item.get('id') or item.get('product_id') or item.get('slug') or titulo.replace(' ', '_')
        url = item.get('url') or item.get('store_url') or item.get('product_url')
        imagen = item.get('image') or item.get('image_url') or item.get('img')
        
        precio_actual = self._extraer_precio_actual(item)
        precio_regular = self._extraer_precio_regular(item)
        moneda = self._extraer_moneda(item)
        
        fecha_fin = item.get('end_date') or item.get('endDate') or None
        
        return {
            'id': f"ps_{product_id}",
            'titulo': titulo,
            'descripcion': item.get('description') or item.get('short_description') or "",
            'url': url or f"{self.base_url}/{self._region_real}/",
            'imagen_url': imagen,
            'tienda': 'PlayStation Store',
            'precio_actual': precio_actual if precio_actual is not None else 0,
            'precio_regular': precio_regular if precio_regular is not None else 0,
            'descuento_porcentaje': int(round(descuento)),
            'moneda': moneda,
            'fecha_fin': fecha_fin
        }
    
    def _fallback_ps_plus(self, sales):
        juegos_gratis = []
        
        for sale in sales:
            sale_id = sale.get('id')
            sale_name = sale.get('name', 'PlayStation Sale')
            
            if 'plus' in sale_name.lower() and 'essential' in sale_name.lower():
                info = {
                    'id': f"platprices_sale_{sale_id}",
                    'titulo': sale_name,
                    'descripcion': "PlayStation Plus Essential - Juegos gratis del mes",
                    'inicio': datetime.now().isoformat(),
                    'fin': None,
                    'url': f"{self.base_url}/{self._region_real}/news/{sale_id}",
                    'imagen': None,
                    'tienda': 'PlayStation Store (PS Plus)'
                }
                juegos_gratis.append(info)
        
        return juegos_gratis


# Test
if __name__ == "__main__":
    hunter = PlatPricesHunter()
    juegos = hunter.obtener_juegos_gratis()
    ofertas = hunter.obtener_ofertas_descuento()
    print(f"\n🎮 Gratis: {len(juegos)} | Ofertas: {len(ofertas)}")
    for juego in juegos[:5]:
        print(f"  ✅ {juego['titulo']}")
    for oferta in ofertas[:5]:
        print(f"  💰 {oferta['titulo']} ({oferta.get('descuento_porcentaje', 0)}%)")
