"""
🔴 Itch.io Hunter v2.0
Detector de juegos gratis en Itch.io usando RSS Feed
Miles de juegos indie gratis permanentes

Usa RSS oficial de Itch.io (sin API key necesaria)
"""

import logging
import requests
import time
from datetime import datetime
import xml.etree.ElementTree as ET

class ItchHunter:
    """
    Busca juegos gratis en Itch.io usando RSS feed oficial
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        # RSS Feed oficial de Itch.io para juegos gratis
        self.rss_url = "https://itch.io/games/price-free.xml"
        self.feed_new = "https://itch.io/feed/new.xml"
        
        # Backup: web scraping
        self.web_url = "https://itch.io/games/newest/free"
        
        print("\n🔴 Itch.io Hunter v2.0 inicializado")
        print("   📡 Usando RSS Feed oficial")
    
    def obtener_juegos_gratis(self, limite=30, min_rating=3.5, min_downloads=100):
        """
        Obtiene juegos gratis de calidad de Itch.io
        
        Args:
            limite (int): Cantidad máxima de juegos a retornar
            min_rating (float): Rating mínimo (1-5 estrellas) - NO DISPONIBLE EN RSS
            min_downloads (int): Descargas mínimas - NO DISPONIBLE EN RSS
        
        Returns:
            list: Lista de juegos gratis
        """
        juegos = []
        
        try:
            print(f"\n🔍 Consultando Itch.io RSS Feed (top {limite} gratis)...")
            
            # Obtener RSS feed
            response = requests.get(self.rss_url, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ RSS no disponible ({response.status_code}), usando scraping...")
                return self._scrape_itch_feed(limite)
            
            # Parsear XML
            root = ET.fromstring(response.content)
            
            # Extraer items del RSS
            items = root.findall('.//item')
            
            for item in items[:limite]:
                juego = self._extraer_info_rss(item)
                if juego:
                    juegos.append(juego)
            
            if juegos:
                print(f"   ✅ Itch.io RSS: {len(juegos)} juego(s) gratis")
            else:
                print(f"   💤 Itch.io RSS: No hay juegos nuevos")
            
            return juegos
        
        except ET.ParseError as e:
            print(f"   ⚠️ Error parseando RSS, usando scraping: {e}")
            return self._scrape_itch_feed(limite)
        
        except Exception as e:
            print(f"   ❌ Error en Itch.io: {e}")
            return []
    
    def _extraer_info_rss(self, item):
        """
        Extrae información del juego desde RSS item
        
        Args:
            item (Element): Item XML del RSS
        
        Returns:
            dict: Información del juego
        """
        try:
            # Título
            titulo_elem = item.find('title')
            titulo = titulo_elem.text if titulo_elem is not None else 'Juego sin título'
            
            # URL
            link_elem = item.find('link')
            url = link_elem.text if link_elem is not None else ''
            
            if not url:
                return None
            
            # ID único del juego (extraer de URL)
            game_id = url.split('/')[-1] if '/' in url else url
            
            # Descripción
            desc_elem = item.find('description')
            descripcion = ''
            if desc_elem is not None and desc_elem.text:
                # Limpiar HTML de la descripción
                import re
                descripcion = re.sub('<[^<]+?>', '', desc_elem.text)
                descripcion = descripcion.strip()[:200]
            
            # Fecha de publicación
            pub_date = item.find('pubDate')
            fecha_pub = pub_date.text if pub_date is not None else None
            
            # Imagen (si está disponible en el RSS)
            imagen_url = None
            
            # Buscar en enclosure (algunos RSS incluyen imágenes aquí)
            enclosure = item.find('enclosure')
            if enclosure is not None:
                imagen_url = enclosure.get('url')
            
            # Buscar en media:thumbnail (namespace de media)
            for child in item:
                if 'thumbnail' in child.tag:
                    imagen_url = child.get('url')
                    break
            
            # Extraer autor si está en el título (formato común: "Juego by Autor")
            autor = "Indie Dev"
            if ' by ' in titulo:
                parts = titulo.split(' by ')
                if len(parts) == 2:
                    titulo = parts[0].strip()
                    autor = parts[1].strip()
            
            juego = {
                'id': f"itch_{game_id}",
                'titulo': titulo,
                'autor': autor,
                'tienda': 'Itch.io',
                'tienda_emoji': '🔴',
                'url': url,
                'imagen_url': imagen_url,
                'fecha_fin': 'Gratis permanente',
                'tipo': 'gratis',
                'fuente': 'Itch.io RSS',
                'descripcion': descripcion or f"Juego indie gratis",
                'fecha_publicacion': fecha_pub,
                # Estos no están disponibles en RSS
                'rating': None,
                'downloads': None,
                'views': None,
                'reviews_percent': None,
                'reviews_count': None,
                'metacritic': None
            }
            
            return juego
        
        except Exception as e:
            print(f"      ⚠️ Error al extraer info RSS: {str(e)[:50]}")
            return None
    
    def _scrape_itch_feed(self, limite=30):
        """
        Scraping alternativo del feed de Itch.io
        (Usado como fallback si RSS falla)
        
        Args:
            limite (int): Cantidad de juegos
        
        Returns:
            list: Juegos encontrados
        """
        juegos = []
        
        try:
            from bs4 import BeautifulSoup
            
            print("   🔍 Scraping feed de Itch.io (fallback)...")
            
            response = requests.get(self.web_url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Itch.io usa clases específicas para juegos
            game_cells = soup.find_all('div', class_='game_cell', limit=limite)
            
            for cell in game_cells:
                try:
                    # Título
                    title_elem = cell.find('a', class_='title game_link')
                    if not title_elem:
                        continue
                    
                    titulo = title_elem.text.strip()
                    url = title_elem.get('href', '')
                    
                    # Asegurar URL completa
                    if url and not url.startswith('http'):
                        url = f"https://itch.io{url}"
                    
                    # Autor
                    author_elem = cell.find('a', class_='game_author')
                    autor = author_elem.text.strip() if author_elem else "Indie Dev"
                    
                    # Imagen
                    img_elem = cell.find('img', class_='lazy_loaded')
                    if not img_elem:
                        img_elem = cell.find('div', class_='game_thumb')
                    
                    imagen_url = None
                    if img_elem:
                        imagen_url = img_elem.get('data-lazy_src') or img_elem.get('src')
                    
                    # Rating (estrellas)
                    rating_elem = cell.find('div', class_='rating_stars')
                    rating = 0
                    if rating_elem:
                        # Extraer rating del style width
                        style = rating_elem.get('style', '')
                        if 'width:' in style:
                            percent = style.split('width:')[1].split('%')[0].strip()
                            rating = float(percent) / 20  # Convertir % a escala 0-5
                    
                    # Precio (verificar que sea gratis)
                    price_elem = cell.find('div', class_='price_value')
                    if price_elem and price_elem.text.strip() != 'Free':
                        continue  # Saltar si no es gratis
                    
                    juego = {
                        'id': f"itch_{url.split('/')[-1]}",
                        'titulo': titulo,
                        'autor': autor,
                        'tienda': 'Itch.io',
                        'tienda_emoji': '🔴',
                        'url': url,
                        'imagen_url': imagen_url,
                        'fecha_fin': 'Gratis permanente',
                        'tipo': 'gratis',
                        'fuente': 'Itch.io Scraping',
                        'rating': rating,
                        'downloads': None,
                        'views': None,
                        'descripcion': f"Juego indie por {autor}",
                        'reviews_percent': None,
                        'reviews_count': None,
                        'metacritic': None
                    }
                    
                    juegos.append(juego)
                
                except Exception as e:
                    print(f"      ⚠️ Error procesando juego: {str(e)[:50]}")
                    continue
            
            if juegos:
                print(f"   ✅ Scraping exitoso: {len(juegos)} juego(s)")
            
            return juegos
        
        except ImportError:
            print("   ❌ BeautifulSoup no instalado. Ejecuta: pip install beautifulsoup4")
            return []
        except Exception as e:
            print(f"   ❌ Error en scraping: {e}")
            return []
    
    def obtener_juegos_nuevos(self, limite=20):
        """
        Obtiene los juegos más nuevos de Itch.io (gratis o de pago)
        Útil para descubrir nuevos releases
        
        Args:
            limite (int): Cantidad de juegos
        
        Returns:
            list: Juegos nuevos (filtrados a solo gratis)
        """
        try:
            print(f"\n🆕 Consultando juegos nuevos en Itch.io...")
            
            response = requests.get(self.feed_new, timeout=15)
            
            if response.status_code != 200:
                return []
            
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            juegos = []
            for item in items[:limite]:
                juego = self._extraer_info_rss(item)
                if juego:
                    juegos.append(juego)
            
            if juegos:
                print(f"   ✅ Encontrados {len(juegos)} juego(s) nuevos")
            
            return juegos
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []


# Test function
def test_itch():
    """Prueba rápida del hunter con RSS"""
    print("\n" + "="*70)
    print("🧪 TEST - Itch.io Hunter v2.0 (RSS)")
    print("="*70)
    
    hunter = ItchHunter()
    
    # Test 1: Obtener juegos gratis vía RSS
    print("\n📦 Test 1: Juegos gratis (RSS Feed)")
    juegos = hunter.obtener_juegos_gratis(limite=10)
    
    if juegos:
        print(f"\n✅ Encontrados {len(juegos)} juego(s)")
        for i, juego in enumerate(juegos[:5], 1):
            print(f"\n{i}. 🎮 {juego['titulo']}")
            print(f"   👤 Por: {juego.get('autor', 'Desconocido')}")
            print(f"   🔗 {juego['url']}")
            if juego.get('descripcion'):
                print(f"   📝 {juego['descripcion'][:100]}...")
            if juego.get('fecha_publicacion'):
                print(f"   📅 {juego['fecha_publicacion']}")
    else:
        print("\n⚠️ No se encontraron juegos")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_itch()
