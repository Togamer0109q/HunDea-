"""
🔴 Itch.io Hunter - Juegos indie gratis
Busca juegos gratis en Itch.io usando su RSS Feed
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime


class ItchHunter:
    """
    Busca juegos indie gratis en Itch.io
    """
    
    def __init__(self):
        self.rss_urls = [
            "https://itch.io/games/free.xml",
            "https://itch.io/games/new-and-popular/free.xml",
            "https://itch.io/games/top-rated/top-sellers.xml"
        ]
        self.session = requests.Session()
    
    def obtener_juegos_gratis(self):
        """
        Obtiene juegos gratis de Itch.io
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos_gratis = []
        
        try:
            print("🔍 Consultando Itch.io RSS Feed...")
            
            # Headers para evitar bloqueo 403
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = None
            for url in self.rss_urls:
                try:
                    response = self.session.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except Exception:
                    response = None
                    continue
            
            if not response:
                raise Exception("Itch.io RSS no disponible (403/timeout)")
            
            # Parsear XML
            root = ET.fromstring(response.content)
            
            # Iterar sobre items del RSS (máximo 30)
            items = root.findall('.//item')[:30]
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text
                    link = link_elem.text
                    descripcion = desc_elem.text if desc_elem is not None else "Juego indie gratis de Itch.io"
                    
                    # Filtrar assets/soundtracks
                    if any(skip in title.lower() for skip in ['soundtrack', 'ost', 'music', 'asset pack']):
                        continue
                    
                    # Crear info del juego
                    info = {
                        'id': f"itch_{link.split('/')[-1]}",
                        'titulo': title,
                        'descripcion': descripcion[:200] if descripcion else "Juego indie gratis",
                        'inicio': datetime.now().isoformat(),
                        'fin': None,  # Permanente
                        'url': link,
                        'imagen': None,  # RSS no incluye imágenes
                        'tienda': 'Itch.io'
                    }
                    
                    juegos_gratis.append(info)
                    
                except Exception as e:
                    continue
            
            print(f"✅ Itch.io: {len(juegos_gratis)} juego(s) gratis encontrados")
            return juegos_gratis
            
        except Exception as e:
            print(f"❌ Error al consultar Itch.io: {e}")
            return []


# Test
if __name__ == "__main__":
    hunter = ItchHunter()
    juegos = hunter.obtener_juegos_gratis()
    print(f"\n🎮 Total: {len(juegos)} juegos")
    for juego in juegos[:5]:
        print(f"  • {juego['titulo']}")
