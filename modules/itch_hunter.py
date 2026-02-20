"""
🔴 Itch.io Hunter - Juegos indie gratis
Busca juegos gratis en Itch.io usando su RSS Feed
"""

import html
import re
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
        self.plataformas_validas = {
            'windows', 'macos', 'linux', 'android'
        }
    
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
                    
                    title_raw = title_elem.text or ""
                    link = link_elem.text
                    descripcion_raw = desc_elem.text if desc_elem is not None else "Juego indie gratis de Itch.io"
                    
                    # Extraer imagen del HTML si existe
                    imagen_url = self._extraer_imagen_html(descripcion_raw)
                    
                    # Limpiar título y tags
                    titulo, tags = self._limpiar_titulo_y_tags(title_raw)
                    if self._es_demo(titulo, tags):
                        continue
                    
                    # Plataformas
                    plataformas = self._extraer_plataformas(tags)
                    
                    # Limpiar descripción (sin HTML)
                    descripcion = self._limpiar_html(descripcion_raw)
                    descripcion = self._formatear_descripcion(descripcion, plataformas)
                    
                    # Filtrar assets/soundtracks
                    if any(skip in titulo.lower() for skip in ['soundtrack', 'ost', 'music', 'asset pack']):
                        continue
                    
                    # Crear info del juego
                    info = {
                        'id': f"itch_{link.split('/')[-1]}",
                        'titulo': titulo,
                        'descripcion': descripcion[:200] if descripcion else "Juego indie gratis",
                        'inicio': datetime.now().isoformat(),
                        'fin': None,  # Permanente
                        'url': link,
                        'imagen': imagen_url,
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

    def _extraer_imagen_html(self, html_text):
        if not html_text:
            return None
        match = re.search(r'<img[^>]+src="([^"]+)"', html_text, re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))
        match = re.search(r"<img[^>]+src='([^']+)'", html_text, re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))
        return None

    def _limpiar_html(self, html_text):
        if not html_text:
            return ""
        # Quitar tags HTML
        text = re.sub(r"<[^>]+>", " ", html_text)
        text = html.unescape(text)
        return " ".join(text.split()).strip()

    def _limpiar_titulo_y_tags(self, titulo):
        tags = re.findall(r"\[([^\]]+)\]", titulo)
        titulo_limpio = re.sub(r"\s*\[[^\]]+\]\s*", " ", titulo)
        titulo_limpio = " ".join(titulo_limpio.split()).strip()
        return titulo_limpio, tags

    def _es_demo(self, titulo, tags):
        if re.search(r"\bdemo\b", titulo, re.IGNORECASE):
            return True
        for tag in tags:
            if re.search(r"demo", tag, re.IGNORECASE):
                return True
        return False

    def _extraer_plataformas(self, tags):
        plataformas = []
        for tag in tags:
            tag_norm = tag.strip().lower()
            if tag_norm in self.plataformas_validas:
                plataformas.append(tag_norm)
        # Orden fijo
        orden = ['windows', 'macos', 'linux', 'android']
        plataformas_ordenadas = [p for p in orden if p in plataformas]
        return plataformas_ordenadas

    def _formatear_descripcion(self, descripcion, plataformas):
        partes = []
        if descripcion:
            partes.append(descripcion)
        if plataformas:
            pretty = ", ".join([p.title() if p != "macos" else "macOS" for p in plataformas])
            partes.append(f"Plataformas: {pretty}")
        return " | ".join(partes).strip()


# Test
if __name__ == "__main__":
    hunter = ItchHunter()
    juegos = hunter.obtener_juegos_gratis()
    print(f"\n🎮 Total: {len(juegos)} juegos")
    for juego in juegos[:5]:
        print(f"  • {juego['titulo']}")
