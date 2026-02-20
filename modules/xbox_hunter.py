"""
🎮 Xbox Hunter - Microsoft Store
Busca juegos gratis y ofertas con descuento usando Microsoft Display Catalog API
"""

import requests
from datetime import datetime


class XboxHunter:
    """
    Busca juegos gratis y ofertas de Xbox usando Microsoft API oficial
    """
    
    def __init__(self, market="US", language="en-US"):
        self.catalog_url = "https://displaycatalog.mp.microsoft.com/v7.0/products"
        self.market = market
        self.language = language
        self.session = requests.Session()
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos GRATIS de Xbox (TopFree catalog)
        
        Returns:
            list: Lista de juegos gratis de Xbox
        """
        juegos_gratis = []
        
        try:
            print("🔍 Consultando Xbox Store (TopFree)...")
            
            products = self._consultar_catalogo("Computed/TopFree", count=50)
            
            for product in products:
                info_precio = self._extraer_precio_y_descuento(product)
                if not info_precio:
                    continue
                
                precio_actual, precio_regular, descuento, moneda, fecha_fin = info_precio
                if not self._es_gratis(descuento, precio_actual):
                    continue
                
                info = self._crear_info_juego(product, precio_actual, precio_regular, descuento, moneda, fecha_fin)
                if info:
                    juegos_gratis.append(info)
            
            print(f"✅ Xbox: {len(juegos_gratis)} juego(s) gratis encontrados")
            return juegos_gratis
            
        except Exception as e:
            print(f"❌ Error al consultar Xbox Store: {e}")
            return []
    
    def obtener_ofertas_descuento(self, descuento_minimo=30, descuento_maximo=99):
        """
        Obtiene ofertas con descuento de Xbox
        
        Args:
            descuento_minimo (int): % mínimo de descuento
            descuento_maximo (int): % máximo de descuento
        
        Returns:
            list: Lista de ofertas con descuento
        """
        ofertas = []
        
        try:
            print("🔍 Consultando Xbox Store (Deals)...")
            
            catalogos = ["Computed/Deal", "Computed/TopPaid"]
            vistos = set()
            
            for catalogo in catalogos:
                products = self._consultar_catalogo(catalogo, count=100)
                for product in products:
                    product_id = product.get('ProductId')
                    if product_id and product_id in vistos:
                        continue
                    if product_id:
                        vistos.add(product_id)
                    
                    info_precio = self._extraer_precio_y_descuento(product)
                    if not info_precio:
                        continue
                    
                    precio_actual, precio_regular, descuento, moneda, fecha_fin = info_precio
                    if descuento is None:
                        continue
                    if descuento < descuento_minimo:
                        continue
                    if descuento > descuento_maximo:
                        continue
                    
                    info = self._crear_info_oferta(product, precio_actual, precio_regular, descuento, moneda, fecha_fin)
                    if info:
                        ofertas.append(info)
            
            print(f"✅ Xbox: {len(ofertas)} oferta(s) encontradas")
            return ofertas
            
        except Exception as e:
            print(f"❌ Error al consultar Xbox Store: {e}")
            return []
    
    def _consultar_catalogo(self, big_catalog_id, count=50):
        params = {
            'market': self.market,
            'languages': self.language,
            'MS-CV': 'DGU1mcuYo0WMMp+F.1',
            'bigCatalogId': big_catalog_id,
            'deviceFamily': 'Windows.Xbox',
            'itemTypes': 'Game',
            'count': count
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = self.session.get(self.catalog_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('Products', [])
        return products if isinstance(products, list) else []
    
    def _extraer_precio_y_descuento(self, product):
        skus = product.get('DisplaySkuAvailabilities', [])
        if not skus:
            return None
        
        for sku in skus:
            availabilities = sku.get('Availabilities', [])
            for availability in availabilities:
                order_mgmt = availability.get('OrderManagementData', {})
                price = order_mgmt.get('Price') or availability.get('Price') or {}
                
                list_price = price.get('ListPrice')
                msrp = price.get('MSRP') or price.get('OriginalPrice') or price.get('BasePrice')
                sale_price = price.get('SalePrice') or list_price
                currency = price.get('CurrencyCode') or price.get('Currency') or 'USD'
                discount = price.get('DiscountPercentage')
                
                if discount is None and msrp and sale_price is not None:
                    if msrp > 0:
                        discount = round(((msrp - sale_price) / msrp) * 100, 1)
                
                if sale_price is None and list_price is not None:
                    sale_price = list_price
                
                if sale_price is None and msrp is not None:
                    sale_price = msrp
                
                if list_price is None and msrp is not None:
                    list_price = msrp
                
                end_date = availability.get('Conditions', {}).get('EndDate')
                
                if sale_price is None and discount is None:
                    continue
                
                return sale_price, msrp or list_price, discount, currency, end_date
        
        return None
    
    def _es_gratis(self, descuento, precio_actual):
        if descuento is not None and descuento >= 100:
            return True
        if precio_actual is not None and precio_actual == 0:
            return True
        return False
    
    def _crear_info_juego(self, product, precio_actual, precio_regular, descuento, moneda, fecha_fin):
        title = product.get('LocalizedProperties', [{}])[0].get('ProductTitle', 'Unknown')
        product_id = product.get('ProductId', '')
        
        localized = product.get('LocalizedProperties', [{}])[0]
        description = localized.get('ShortDescription', 'Juego gratis de Xbox')
        image_url = self._extraer_imagen(localized.get('Images', []))
        
        return {
            'id': f"xbox_{product_id}",
            'titulo': title,
            'descripcion': description[:200] if description else "Juego gratis de Xbox",
            'inicio': datetime.now().isoformat(),
            'fin': fecha_fin,
            'url': f"https://www.xbox.com/{self.language.lower()}/games/store/a/{product_id}",
            'imagen': image_url,
            'tienda': 'Xbox Store (Free)'
        }
    
    def _crear_info_oferta(self, product, precio_actual, precio_regular, descuento, moneda, fecha_fin):
        title = product.get('LocalizedProperties', [{}])[0].get('ProductTitle', 'Unknown')
        product_id = product.get('ProductId', '')
        
        localized = product.get('LocalizedProperties', [{}])[0]
        description = localized.get('ShortDescription', '')
        image_url = self._extraer_imagen(localized.get('Images', []))
        
        return {
            'id': f"xbox_{product_id}",
            'titulo': title,
            'descripcion': description[:200] if description else "",
            'url': f"https://www.xbox.com/{self.language.lower()}/games/store/a/{product_id}",
            'imagen_url': image_url,
            'tienda': 'Xbox Store',
            'precio_actual': precio_actual if precio_actual is not None else 0,
            'precio_regular': precio_regular if precio_regular is not None else 0,
            'descuento_porcentaje': int(round(descuento)) if descuento is not None else 0,
            'moneda': moneda,
            'fecha_fin': fecha_fin
        }
    
    def _extraer_imagen(self, images):
        for img in images:
            if img.get('ImagePurpose') in ['Poster', 'BoxArt', 'SuperHeroArt']:
                return img.get('Uri')
        if images:
            return images[0].get('Uri')
        return None


# Test
if __name__ == "__main__":
    hunter = XboxHunter(market="MX", language="es-MX")
    juegos = hunter.obtener_juegos_gratis()
    ofertas = hunter.obtener_ofertas_descuento()
    print(f"\n🎮 Gratis: {len(juegos)} | Ofertas: {len(ofertas)}")
    for juego in juegos[:5]:
        print(f"  ✅ {juego['titulo']}")
    for oferta in ofertas[:5]:
        print(f"  💰 {oferta['titulo']} ({oferta.get('descuento_porcentaje', 0)}%)")
