"""
🎮 Console Hunter - Deals de Xbox
Busca deals de Xbox usando CheapShark API
"""

import requests
from datetime import datetime


class ConsoleHunter:
    """
    Busca deals de Xbox
    """
    
    def __init__(self, min_discount=50):
        self.min_discount = min_discount
        self.cheapshark_url = "https://www.cheapshark.com/api/1.0/deals"
        self.xbox_store_id = "30"  # Microsoft Store en CheapShark
    
    def obtener_xbox_deals(self):
        """
        Obtiene deals de Xbox desde CheapShark
        
        Returns:
            list: Lista de deals de Xbox
        """
        deals = []
        
        try:
            print("🔍 Consultando Xbox deals (CheapShark)...")
            
            # Parámetros para CheapShark
            params = {
                'storeID': self.xbox_store_id,
                'upperPrice': 0,  # Solo gratis
                'pageSize': 60
            }
            
            response = requests.get(self.cheapshark_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data:
                try:
                    title = item.get('title', 'Unknown Game')
                    normal_price = float(item.get('normalPrice', 0))
                    sale_price = float(item.get('salePrice', 0))
                    savings = float(item.get('savings', 0))
                    
                    # Solo deals con descuento mínimo
                    if savings < self.min_discount:
                        continue
                    
                    # URL del deal
                    deal_id = item.get('dealID', '')
                    url = f"https://www.cheapshark.com/redirect?dealID={deal_id}"
                    
                    # Imagen
                    thumb = item.get('thumb', None)
                    
                    # Crear info del deal
                    info = {
                        'id': f"xbox_{deal_id}",
                        'titulo': title,
                        'descripcion': f"Xbox deal con {int(savings)}% de descuento",
                        'inicio': datetime.now().isoformat(),
                        'fin': None,
                        'url': url,
                        'imagen': thumb,
                        'tienda': 'Xbox (Microsoft Store)',
                        'precio_original': normal_price,
                        'precio_actual': sale_price,
                        'descuento': int(savings)
                    }
                    
                    deals.append(info)
                    
                except Exception as e:
                    continue
            
            print(f"✅ Xbox: {len(deals)} deal(s) encontrados (>{self.min_discount}% off)")
            return deals
            
        except Exception as e:
            print(f"❌ Error al consultar Xbox deals: {e}")
            return []
    
    def obtener_juegos_gratis(self):
        """
        Alias para compatibilidad con v3
        """
        return self.obtener_xbox_deals()


# Test
if __name__ == "__main__":
    hunter = ConsoleHunter(min_discount=50)
    deals = hunter.obtener_xbox_deals()
    print(f"\n🎮 Total: {len(deals)} deals de Xbox")
    for deal in deals[:5]:
        print(f"  • {deal['titulo']} ({deal['descuento']}% off)")
